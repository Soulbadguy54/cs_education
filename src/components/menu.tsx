import {Link, Route, Routes, useNavigate} from 'react-router-dom';
import React, {useEffect, useRef, useState} from 'react';
import {
    activeOverlays,
    appColors,
    appSizeI,
    currentTheme,
    gridElementParamsI,
    mapIcons,
    themeColorsObject
} from '../extra/Interfaces';
import {backButton} from "@telegram-apps/sdk";
import {
    closingBehavior,
    getCloudStorageItem,
    hideBackButton,
    init,
    initData, isCloudStorageSupported, isTMA,
    miniApp, setCloudStorageItem,
    swipeBehavior,
    themeParams,
    User, useSignal,
    viewport,
} from '@telegram-apps/sdk-react';
import wrenchIcon from '../assets/other/wrench_icon.webp';
import '../styles/menu.css';
import MainComponent from "./main";
import {checkUserInitData} from "../extra/apiRequests";
import {maps} from "../extra/enums";
import LoadOverlay from "./loading";
import TelegramRequiredComponent from "./errorPages";
import SubscribePopup from "./otherPopups";
import {AnimatePresence} from "framer-motion";


const commonImages = [
    ...Object.values(mapIcons),
    wrenchIcon,
];

const validMaps = [maps.MIRAGE, maps.DUST2, maps.OVERPASS, maps.ANCIENT, maps.INFERNO, maps.TRAIN, maps.ANUBIS]


let TELEGRAM_AVAILABLE = true;
if (isTMA()) {
    init();
    initData.restore()
    closingBehavior.mount()
    swipeBehavior.mount()
    viewport.mount()
    backButton.mount()
} else {
    TELEGRAM_AVAILABLE = false;
}


function Home() {
    const [stablePageSize, setStablePageSize] = useState<appSizeI>({
        height: viewport.stableHeight(), width: viewport.width()
    });
    const [gridElementParams, setGridElementParams] = useState<gridElementParamsI>({
        tileSize: 0, gapSize: 0, paddingSize: 0
    })

    const [overlay, setOverlay] = useState<activeOverlays>({
        loading: true,
        info: false,
        homeScreen: false,
        channel_subscribe: false,
    });
    const [themeColors, setThemeColors] = useState<themeColorsObject>(() => {
        if (currentTheme.type) {
            return currentTheme.type === 'dark' ? appColors.dark : appColors.light
        } else {
            return themeParams.isDark() ? appColors.dark : appColors.light
        }
    });
    const userDataFromTg = useRef<User | undefined>(initData?.user())
    const navigate = useNavigate(); // Хук для перенаправления
    const heightChangedTo = useSignal(viewport.stableHeight)
    const widthChangedTo = useSignal(viewport.width)

    useEffect(() => {
        if (!TELEGRAM_AVAILABLE) {
            navigate('/telegram-required');
        }
    }, [navigate]);

    const processUserData = async () => {
        if (isCloudStorageSupported()) {
            getCloudStorageItem('theme').then(
                (storedTheme) => {
                    if (storedTheme === '') {
                        setCloudStorageItem('theme', themeColors.type);
                        currentTheme.type = themeColors.type;
                    } else {
                        setThemeColors(() => (storedTheme === 'dark' ? appColors.dark : appColors.light))
                        currentTheme.type = storedTheme;
                    }
                }
            )
        }

        if (!userDataFromTg.current?.id) return;

        const dataFromServer = await checkUserInitData(initData.raw())
        await setCloudStorageItem('access_token', dataFromServer.access_token)
        await setCloudStorageItem('is_subscribed',dataFromServer.is_subscribed.toString())
    }

    const loadData = async () => {
        const commonImagePromises = commonImages.map(src => {
            return new Promise((resolve) => {
                const img = new Image();
                img.src = src;
                img.onload = resolve;
                img.onerror = resolve;
            });
        });

        await Promise.all([...commonImagePromises, processUserData()]);
    };

    useEffect(() => {
        miniApp.ready.ifAvailable()
        setOverlay((prev) => ({...prev, loading: true}))
        const startTime = Date.now();
        const minLoadingTime = 500;

        loadData()
            .then(() => {
                if (miniApp.mountSync.isAvailable()) {
                    miniApp.mountSync();
                }
                if (miniApp.setHeaderColor.isAvailable()) {
                    miniApp.setHeaderColor(themeColors.headerColor);
                }
                hideBackButton.ifAvailable();
                setStablePageSize({height: viewport.stableHeight(), width: viewport.width()});

                const params = new URLSearchParams(window.location.hash.slice(1));
                setCloudStorageItem('platform', params.get('tgWebAppPlatform') || "");

                const elapsed = Date.now() - startTime;
                if (elapsed < minLoadingTime) {
                    return new Promise((resolve) => setTimeout(resolve, minLoadingTime - elapsed));
                }
            })
            .then(() => setOverlay((prev) => ({ ...prev, loading: false })))
            .catch((error) => {
                console.error('Error loading data:', error);
                setOverlay((prev) => ({ ...prev, loading: false })); // Убираем загрузку даже при ошибке
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

    useEffect(() => {
        if (!miniApp.isActive()) return;

        const height = viewport.stableHeight()
        const width = viewport.width()

        setStablePageSize({height: height, width: width})

        const paddingPart = 0.03;
        const gapPart = 0.03;

        const tileWidth: number = Math.floor((width - 2 * width * paddingPart - width * gapPart) / 2)
        const tileHeight: number = Math.floor((height - 2 * height * paddingPart - 3 * height * gapPart) / 4)
        if (tileWidth > tileHeight) {
            setGridElementParams({tileSize: tileHeight, gapSize: Math.floor(height * gapPart), paddingSize: Math.floor(height * paddingPart - 2)})
        } else {
            setGridElementParams({tileSize: tileWidth, gapSize: Math.floor(width * gapPart), paddingSize: Math.floor(width * paddingPart - 2)})
        }
    }, [heightChangedTo, widthChangedTo]);

    return (
        <div
            className="app-container"
            key={"app-container"}
            style={{
                height: stablePageSize.height,
                width: stablePageSize.width,
            }}
        >
            <AnimatePresence>
                {overlay.loading && (<LoadOverlay/>)}
            </AnimatePresence>
            <AnimatePresence>
                {overlay.channel_subscribe && (<SubscribePopup themeColors={themeColors} userLanguage={initData.user()?.language_code || 'eng'}/>)}
            </AnimatePresence>
            <div
                className="grid-container"
                key={"grid-container"}
                style={{
                    height: stablePageSize.height,
                    backgroundColor: themeColors.secondaryBgColor,
                    padding: gridElementParams.paddingSize,
                    gap: gridElementParams.gapSize,
                }}
            >
                {validMaps.map((mapName) => (
                    <Link
                        key={mapName}
                        to={`/${mapName.toLowerCase()}?map=${mapName}`}
                    >
                        <div
                            key={`${mapName}_div`}
                            className="grid-tile"
                            style={{
                                background: themeColors.bgColor,
                                width: gridElementParams.tileSize,
                                height: gridElementParams.tileSize
                            }}
                        >
                            <img src={mapIcons[mapName]} alt={mapName} key={`${mapName}_img`}/>
                        </div>
                    </Link>
                ))}
                {[maps.NUKE].map(mapName => (
                    <div
                        className="grid-tile disabled"
                        key={`${mapName}_div`}
                        style={{
                            background: themeColors.bgColor,
                            width: gridElementParams.tileSize,
                            height: gridElementParams.tileSize
                        }}
                    >
                        <img src={mapIcons[mapName]} alt={mapName} key={`${mapName}_img`}/>
                        <img src={wrenchIcon} className="wrench-icon" alt={"wrench"} key={"wrench"}/>
                    </div>
                ))}
            </div>
        </div>
    );
}


export default function Menu() {
    return (
        <Routes>
            <Route
                key={`home`}
                path="/"
                element={<Home />}
            />
            {validMaps.map(mapName => {
                return (
                    <Route
                        key={`${mapName}_route`}
                        path={`/${mapName.toLowerCase()}`}
                        element={<MainComponent />}
                    />
                )
            })}
            <Route
                key={`tg_required`}
                path="/telegram-required"
                element={<TelegramRequiredComponent />}
            />
        </Routes>
    );
}