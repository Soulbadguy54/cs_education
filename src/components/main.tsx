import {FC, useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {useLocation, useNavigate} from "react-router-dom";
import {backButton, initData} from '@telegram-apps/sdk';
import {
    getCloudStorageItem, isTMA,
    miniApp, setCloudStorageItem,
    showBackButton,
    themeParams, useSignal,
    viewport
} from "@telegram-apps/sdk-react";
import {
    appColors,
    activeOverlays,
    dotImages,
    filterImages,
    filterTypes,
    grenadeImages,
    likedDotImages,
    mapRadarImages,
    themeColorsObject,
    Grenade,
    instructionImages,
    appDataI,
    actionsI,
    appSizeI,
    currentTheme
} from '../extra/Interfaces';
import {grenadeSides, grenadeTypes, maps, themes} from "../extra/enums";
import {checkUserInitData, fetchGrenadesFromDb} from '../extra/apiRequests';
import '../styles/main.css';
import MapContainer from "./map";
import favouriteIcon from "../assets/other/favourite_v2.webp"
import themeIcon from '../assets/other/change_theme.webp'
import themeIconAnimated from '../assets/other/change_theme_animated.webp'
import LoadOverlay from "./loading";
import InfoOverlay from "./info";
import infoIcon from "../assets/other/info.webp";
import {AnimatePresence, motion} from "framer-motion";
import SwitchContainer from "./switch";


const commonImages = [
    ...Object.values(grenadeImages),
    ...Object.values(filterImages),
    ...Object.values(likedDotImages),
    ...Object.values(dotImages),
    ...Object.values(instructionImages),
    infoIcon, themeIcon, themeIconAnimated,
];

let TELEGRAM_AVAILABLE = true;
if (!isTMA()) {
    TELEGRAM_AVAILABLE = false;
}


const MainComponent: FC = () => {
    const [stablePageSize, setStablePageSize] = useState<appSizeI>({
        height: viewport.stableHeight(), width: viewport.width()
    });
    const [controlImgParams, setControlImgParams] = useState({gap: 0, size: 0});

    const opacityValues = useRef({'visible': 1, 'invisible': 0.2})

    const [themeColors, setThemeColors] = useState<themeColorsObject>(() => {
        if (currentTheme.type) {
            return currentTheme.type === 'dark' ? appColors.dark : appColors.light
        } else {
            return themeParams.isDark() ? appColors.dark : appColors.light
        }
    });

    const [visibleGrenades, setVisibleGrenades] = useState<{[key: string]: Grenade[]}>({});
    const [overlay, setOverlay] = useState<activeOverlays>({
        loading: true,
        info: false,
        homeScreen: false,
        channel_subscribe: false,
    });
    const [visibleTypes, setVisibleTypes] = useState<filterTypes>({
        type: {
            [grenadeTypes.SMOKE]: false,
            [grenadeTypes.MOLOTOV]: false,
            [grenadeTypes.HE]: false,
            [grenadeTypes.FLASH]: false,
        },
        side: {
            [grenadeSides.CT]: false,
            [grenadeSides.T]: false,
        },
        is_favourite: false,
        difficulty: 3,
        activeFinalPosId: null,
        extraFilter: null,
    });
    const appData = useRef<appDataI>({
        grenades: {},
        current_map: new URLSearchParams(useLocation().search).get("map") || maps.MIRAGE,
        userDataFromTg: initData?.user(),
        info_clicked: true,
        access_token: "",
        platform: "",
    });

    const appActions = useRef<actionsI>({
        themeChanging: false,
    });
    const navigate = useNavigate();
    const heightChangedTo = useSignal(viewport.stableHeight)
    const widthChangedTo = useSignal(viewport.width)

    useEffect(() => {
        if (!TELEGRAM_AVAILABLE) {
            navigate('/telegram-required');
        }
    }, [navigate]);

    useEffect(() => {
        if (!miniApp.isActive()) return;

        const height = viewport.stableHeight()
        const width = viewport.width()

        setStablePageSize({height: height, width: width})

        let size = (height - height * 0.1 - width) / 2 * 0.55
        let gap = size * 0.25
        if ((size * 4 + gap * 5) > width) {
            size = width / 5.25
            gap = size * 0.25
        }
        setControlImgParams({gap: gap, size: size});
    }, [heightChangedTo, widthChangedTo]);

    const processUserData = async () => {
        getCloudStorageItem(['theme', 'is_favourite', 'info_clicked',]).then(
            (cloudData) => {
                appData.current.info_clicked = cloudData.info_clicked === 'true';
                if (cloudData.theme === '') {
                    setCloudStorageItem('theme', themeColors.type)
                    currentTheme.type = themeColors.type;
                } else {
                    setThemeColors(() => (cloudData.theme === 'dark' ? appColors.dark : appColors.light))
                    currentTheme.type = cloudData.theme;
                }

                if (cloudData.is_favourite) {
                    setVisibleTypes((prev) => ({...prev, is_favourite: cloudData.is_favourite === 'true'}));
                } else {
                    setCloudStorageItem('is_favourite', visibleTypes.is_favourite? 'true': 'false')
                }
            }
        )
        getCloudStorageItem([grenadeTypes.SMOKE, grenadeTypes.HE, grenadeTypes.MOLOTOV, grenadeTypes.FLASH,]).then(
            (cloudData) => {
                Object.entries(cloudData).forEach(([filterName, filterValue]) => {
                    if (filterValue) {
                        setVisibleTypes((prev) => ({...prev, type: {...prev.type, [filterName]: filterValue === 'true'}}));
                    } else {
                        setVisibleTypes((prev) => ({...prev, type: {...prev.type, [filterName]: true}}));
                        setCloudStorageItem(filterName, 'true')
                    }
                })
            }
        )
        getCloudStorageItem([grenadeSides.T, grenadeSides.CT,]).then(
            (cloudData) => {
                Object.entries(cloudData).forEach(([filterName, filterValue]) => {
                    if (filterValue) {
                        setVisibleTypes((prev) => ({...prev, side: {...prev.side, [filterName]: filterValue === 'true'}}));
                    } else {
                        setVisibleTypes((prev) => ({...prev, side: {...prev.side, [filterName]: true}}));
                        setCloudStorageItem(filterName, 'true')
                    }
                })
            }
        )
        getCloudStorageItem('platform').then(platform => appData.current.platform = platform)

        if (!appData.current.userDataFromTg?.id) return;

        const dataFromServer = await checkUserInitData(initData.raw())
        await setCloudStorageItem('access_token', dataFromServer.access_token)
        await setCloudStorageItem('is_subscribed',dataFromServer.is_subscribed.toString())
    }

    const loadData = async () => {
        const mapImagePromise = new Promise((resolve) => {
            const img = new Image();
            img.src = mapRadarImages[appData.current.current_map];
            img.onload = resolve;
            img.onerror = resolve;
        });

        const commonImagePromises = commonImages.map(src => {
            return new Promise((resolve) => {
                const img = new Image();
                img.src = src;
                img.onload = resolve;
                img.onerror = resolve;
            });
        });

        await Promise.all([
            mapImagePromise,
            ...commonImagePromises,
            processUserData(),
        ]);

        appData.current.grenades = await fetchGrenadesFromDb(appData.current.current_map, appData.current.userDataFromTg?.id)
        setVisibleGrenades(getVisibleGrenades(visibleTypes, appData.current.grenades, filterGrenades))
    };

    useEffect(() => {
        miniApp.ready.ifAvailable()
        setOverlay((prev) => ({...prev, loading: true}))
        const startTime = Date.now();
        const minLoadingTime = 500;

        const finalize = () => {
            setOverlay((prev) => ({ ...prev, loading: false }));
            if (!appData.current.info_clicked) {
                setOverlay((prev) => ({ ...prev, info: true }));
                appData.current.info_clicked = true;
                setCloudStorageItem('info_clicked', 'true').catch((error) =>
                    console.error('Error saving info_clicked:', error)
                );
            }
        };

        loadData()
            .then(() => {
                backButton.mount.ifAvailable();
                showBackButton.ifAvailable();
                if (backButton.onClick.isAvailable()) {
                    backButton.onClick(() => {window.history.back()});
                }
                if (miniApp.setHeaderColor.isAvailable()) {
                    miniApp.setHeaderColor(themeColors.headerColor);
                }

                const elapsed = Date.now() - startTime;
                if (elapsed < minLoadingTime) {
                    return new Promise((resolve) => setTimeout(resolve, minLoadingTime - elapsed));
                }
            })
            .then(finalize)
            .catch((error) => {
                console.error('Error loading data:', error);
                finalize(); // Убираем загрузку даже при ошибке
            })
            .then(() => {
                getCloudStorageItem('is_subscribed').then(
                    (isSubscribed) => {
                        if (!(isSubscribed === 'true')) {
                            setOverlay((prev) => ({ ...prev, channel_subscribe: true }))
                        }
                    }
                )
            });
    }, []);

  const themeSwitchAnimation = {
      'bgColor': {
          initial: {backgroundColor: themeColors.bgColor},
          animate: {backgroundColor: themeColors.bgColor},
          transition: { duration: 0.4, ease: 'easeOut' }
      },
      'secondaryBgColor': {
          initial: {backgroundColor: themeColors.secondaryBgColor},
          animate: {backgroundColor: themeColors.secondaryBgColor},
          transition: { duration: 0.4, ease: 'easeOut' }
      },
  }

  const filterGrenades = useCallback(
      (grenades: {[key: string]: Grenade}) => {
          return Object.values(grenades).filter(grenade =>
              visibleTypes.type[grenade.type] &&
              visibleTypes.side[grenade.side] &&
              visibleTypes.difficulty >= grenade.difficult &&
              (!visibleTypes.is_favourite || grenade.is_favourite) &&
              (!visibleTypes.extraFilter || grenade.type === visibleTypes.extraFilter)
          );
  }, [visibleTypes]);

  const getVisibleGrenades = (
      visibleTypes: filterTypes,
      grenades: { [key: string]: {[key: string]: Grenade} },
      filterGrenades: (grenades: { [key: string]: Grenade }) => Grenade[]
  ) => {
      const currentActivePosId = visibleTypes.activeFinalPosId;
      const newObj: {[key: string]: Grenade[]} = {};

      if (currentActivePosId) {
          const grenadesDict = grenades[currentActivePosId];
          newObj[currentActivePosId] = filterGrenades(grenadesDict);
      } else {
          Object.entries(grenades).forEach(([finalPosKey, grenadesDict]) => {
              const filteredGrenades = filterGrenades(grenadesDict);
              if (filteredGrenades.length > 0) {
                  newObj[finalPosKey] = filteredGrenades;
              }
          });
      }
      return newObj;
  };

  const memoVisibleGrenades = useMemo(
      () => getVisibleGrenades(visibleTypes, appData.current.grenades, filterGrenades),
      [visibleTypes, appData.current.grenades, filterGrenades]
  );

  useEffect(() => {
      setVisibleGrenades(memoVisibleGrenades)
  }, [memoVisibleGrenades]);

  return (
      <div
          style={{
              height: stablePageSize.height,
              width: stablePageSize.width,
              display: 'flex',
              flexDirection: 'column'}}
      >
        <AnimatePresence>
            {overlay.loading && (<LoadOverlay/>)}
        </AnimatePresence>
        <AnimatePresence>
          {overlay.info && (
              <InfoOverlay overlay={overlay} setOverlay={setOverlay} themeColors={themeColors}
                           stablePageSize={stablePageSize} userLanguage={appData.current.userDataFromTg?.language_code || 'eng'}/>
          )}
        </AnimatePresence>
        <motion.div
            className="top-container"
            {...themeSwitchAnimation["bgColor"]}
        >
          <motion.img
              src={infoIcon}
              key={"infoIcon"}
              className="info-icon"
              whileTap={{
                scale: 1.2,
                rotate: 5,
                transition: {
                  duration: 0.1,
                  ease: "easeInOut",
                }
              }}
              onClick={() => setOverlay((prev) => ({...prev, info: !prev.info}))}
          />
          <SwitchContainer visibleTypes={visibleTypes} setVisibleTypes={setVisibleTypes} themeColors={themeColors}
                           appData={appData} overlay={overlay} setOverlay={setOverlay} themeSwitchAnimation={themeSwitchAnimation}/>
          <img
              id="theme-icon"
              src={themeIcon}
              alt={"Смена темы"}
              key={"themeIcon"}
              className="theme-icon"
              onClick={(e) => {
                  if (overlay.info) {
                      setOverlay((prev) => ({...prev, info: false}))
                      return
                  }
                  if (appActions.current.themeChanging) {
                      return;
                  }
                  appActions.current.themeChanging = true;
                  const target = e.currentTarget
                  target.src = themeIconAnimated;
                  setTimeout(() => {
                      target.src = themeIcon
                      appActions.current.themeChanging = false;
                  },950)
                  setThemeColors((prev) => {
                      const newColor = prev.type === themes.DARK ? appColors[themes.LIGHT] : appColors[themes.DARK]
                      setCloudStorageItem('theme', newColor.type);
                      currentTheme.type = newColor.type;
                      return newColor;
                  }
                      )

              }}
          />
        </motion.div>

        <MapContainer themeColors={themeColors} visibleGrenades={visibleGrenades} appData={appData} stablePageSize={stablePageSize}
                      visibleTypes={visibleTypes}  setVisibleTypes={setVisibleTypes} themeSwitchAnimation={themeSwitchAnimation}/>

        <motion.div id="controls-container" className="controls-container" {...themeSwitchAnimation["bgColor"]}>
          <div
              className="controls"
              style={{
                  gap: controlImgParams.gap,
                  height: controlImgParams.size / 0.7,
              }}>
            {Object.keys(grenadeTypes).map((key: string) => {
              return (
                  <img
                      src={filterImages[grenadeTypes[key]]}
                      alt={grenadeTypes[key]}
                      key={`${grenadeTypes[key]}_filter`}
                      onClick={() => {
                          if (overlay.info) {
                              setOverlay((prev) => ({...prev, info: false}))
                              return
                          }
                          setVisibleTypes((prev) => {
                              setCloudStorageItem(key, !prev.type[key]? 'true': 'false')
                              return {...prev, type: {...prev.type, [key]: !prev.type[key]}, activeFinalPosId: null};
                          });
                      }}
                      className="control-icon"
                      style={{
                          opacity: visibleTypes.type[grenadeTypes[key]] ? opacityValues.current.visible : opacityValues.current.invisible,
                          width: controlImgParams.size,
                          height: controlImgParams.size,
                      }}
                  />
              )
            })}
          </div>
          <div
              className="controls"
              style={{
                  gap: controlImgParams.gap,
                  height: controlImgParams.size / 0.7,
              }}>
            {Object.keys(grenadeSides).map((key: string) => {
              return (
                  <img
                      src={filterImages[grenadeSides[key]]}
                      key={`${grenadeSides[key]}_filter`}
                      alt={grenadeSides[key]}
                      onClick={() => {
                          if (overlay.info) {
                              setOverlay((prev) => ({...prev, info: false}))
                              return
                          }
                          setVisibleTypes((prev) => {
                              setCloudStorageItem(key, !prev.side[key]? 'true': 'false')
                              return {...prev, side: {...prev.side, [key]: !prev.side[key]}, activeFinalPosId: null};
                          });
                      }}
                      className="control-icon"
                      style={{
                          opacity: visibleTypes.side[grenadeSides[key]] ? opacityValues.current.visible : opacityValues.current.invisible,
                          width: controlImgParams.size,
                          height: controlImgParams.size,
                      }}
                  />
              )
            })}
            <img
                src={favouriteIcon}
                id={"favourite_filter"}
                alt={"Favourite"}
                key={"favourite_filter"}
                onClick={() => {
                    if (overlay.info) {
                        setOverlay((prev) => ({...prev, info: false}))
                        return
                    }
                    setVisibleTypes((prev) => {
                        setCloudStorageItem('is_favourite', !prev.is_favourite? 'true': 'false')
                        return {...prev, is_favourite: !prev.is_favourite, activeFinalPosId: null};
                    });
                }}
                className="control-icon"
                style={{
                    opacity: visibleTypes.is_favourite ? opacityValues.current.visible : opacityValues.current.invisible,
                    width: controlImgParams.size,
                    height: controlImgParams.size,
                }}
            />
          </div>
        </motion.div>
      </div>
  );
}

export default MainComponent;