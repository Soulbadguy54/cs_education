import {
    useEffect,
    useRef,
    useState,
    TouchEvent,
    MouseEvent,
    RefObject,
    Dispatch,
    SetStateAction,
    useCallback
} from "react";
import {
    dotImages,
    likedDotImages,
    Grenade,
    mapRadarImages,
    themeColorsObject, filterTypes, appDataI, appSizeI, clickBehaviorI
} from "../extra/Interfaces";
import {motion, AnimatePresence, useAnimate} from 'framer-motion';
import {openTelegramLink} from "@telegram-apps/sdk";
import '../styles/main.css'
import {addOrRemoveGrenadeFromFavourite} from "../extra/apiRequests";
import {TransformComponent, TransformWrapper} from "react-zoom-pan-pinch";
import {InitialPositionComponent, FinalPositionComponent} from "./positions";
import {useDoubleTap} from "use-double-tap";
import GrenadePopupContainer from "./grenadePopup";
import {openLink} from "@telegram-apps/sdk-react";


interface MapContainerProps {
    themeColors: themeColorsObject,
    appData: RefObject<appDataI>,
    visibleTypes: filterTypes,
    setVisibleTypes: Dispatch<SetStateAction<filterTypes>>,
    themeSwitchAnimation: object,
    visibleGrenades: {[key: string]: Grenade[]},
    stablePageSize: appSizeI,
}


function MapContainer (props: MapContainerProps,) {
    const [mapSize, setMapSize] = useState(0);

    const clickBehavior = useRef<clickBehaviorI>({
        cursorPos: {x: 0, y: 0},
        preventClick: false,
    })

    const [grenadePopup, setGrenadePopup] = useState<null | {popupPosition: string}>(null);

    const [, animate] = useAnimate()

    // ---------------------------------------------------- КАРТА ----------------------------------------------------

    useEffect(() => {
        const newSize = Math.min(props.stablePageSize.height, props.stablePageSize.width);
        setMapSize(newSize);
        }, [props.stablePageSize]);

    const handleMapClick = (e: MouseEvent<HTMLDivElement> | TouchEvent<HTMLDivElement>) => {
        if (!(e.target === e.currentTarget)) return;

        if (clickBehavior.current.preventClick) {
            clickBehavior.current.preventClick = false;
            return;
        }

        props.setVisibleTypes((prev) => ({...prev, activeFinalPosId: null, extraFilter: null}));
        setGrenadePopup(null);
    };

    const handlePanningStart = (_, e) => {
        if (e instanceof MouseEvent) {
            clickBehavior.current.cursorPos = { x: e.clientX, y: e.clientY }
        } else if ( e instanceof TouchEvent && e.touches[0]) {
            clickBehavior.current.cursorPos = { x: e.touches[0].clientX, y: e.touches[0].clientY }
        }
    };

    const handlePanningStop = (_, e) => {
        let currentPos;
        const prevPos = clickBehavior.current.cursorPos;
        if (e instanceof MouseEvent) {
            currentPos = { x: e.clientX, y: e.clientY }
        } else if ( e instanceof TouchEvent && e.changedTouches[0]) {
            currentPos = { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY }
        } else return;
        clickBehavior.current.preventClick = currentPos.x !== prevPos.x || currentPos.y !== prevPos.y;
        clickBehavior.current.cursorPos = {x: 0, y: 0}
    };

    // ----------------------------------------- ФИНАЛЬНАЯ ПОЗИЦИЯ ----------------------------------------------------

    const handleClickOnFinalPos = useCallback((e: MouseEvent<HTMLDivElement> | TouchEvent<HTMLDivElement>) => {
        e.stopPropagation();
        if (clickBehavior.current.preventClick) {
            clickBehavior.current.preventClick = false;
            return;
        }

        const positionKey = e.currentTarget.dataset.positionKey
        const extraKey = e.currentTarget.dataset.extraKey
        if (!positionKey) return;

        if (props.visibleTypes.activeFinalPosId === positionKey) {
            if (extraKey) {
                setGrenadePopup(null);
                props.setVisibleTypes((prev) => ({...prev, extraFilter: extraKey}));
            } else {
                props.setVisibleTypes((prev) => ({...prev, activeFinalPosId: null, extraFilter: null}));
            }
        } else {
            props.setVisibleTypes((prev) => ({...prev, activeFinalPosId: positionKey}));
        }
    }, [props.visibleTypes])

    const handleCircleClick = useCallback((e: MouseEvent<HTMLDivElement> | TouchEvent<HTMLDivElement>) => {
        e.stopPropagation();
        if (clickBehavior.current.preventClick) {
            clickBehavior.current.preventClick = false;
            return;
        }

        const positionKey = e.currentTarget.dataset.positionKey
        if (!positionKey) return;

        props.setVisibleTypes((prev) => ({...prev, activeFinalPosId: positionKey}));
        setGrenadePopup({popupPosition: e.currentTarget.style.inset})
    }, [props.visibleTypes])

    // ----------------------------------------- НАЧАЛЬНАЯ ПОЗИЦИЯ ----------------------------------------------------

    const onDoubleTapClick = useCallback(async (e: MouseEvent<Element, globalThis.MouseEvent>) => {
        e.stopPropagation();
        e.preventDefault()

        if (!(e.currentTarget instanceof HTMLDivElement)) return;

        const dataSet = e.currentTarget.dataset

        if (!dataSet.grenadeId) return;

        const target = e.currentTarget.firstChild
        const finalPosId = props.visibleTypes.activeFinalPosId
        if (!(target instanceof HTMLImageElement) || !finalPosId) return;

        try {
            if (!props.appData.current.userDataFromTg?.id) {
                console.error('ID пользователя недоступен');
                return;
            }
            props.appData.current.grenades[finalPosId][dataSet.grenadeId].is_favourite = await addOrRemoveGrenadeFromFavourite(
                props.appData.current.userDataFromTg.id,
                Number(dataSet.grenadeId),
                props.appData.current.grenades[finalPosId][dataSet.grenadeId].is_favourite
            );
        } catch (error) {
            console.error('Ошибка при обработке избранного:', error);
        } finally {
            const grenadeData = props.appData.current.grenades[finalPosId][dataSet.grenadeId];
            target.src = grenadeData.is_favourite ? likedDotImages[grenadeData.difficult] : dotImages[grenadeData.difficult];
            await animate(target, { scale: 0.1, opacity: 0.2 }, { duration: 0.2 });
            await animate(target, { scale: 1, opacity: 1 }, {
                duration: 0.2,
                ease: "easeInOut",
                scale: {
                    type: "spring",
                    stiffness: 200,
                    damping: 15,
                }
            });
        }
    }, [props.visibleTypes.activeFinalPosId, props.appData])

    const onSingleTapClick = useCallback((e: MouseEvent<Element, globalThis.MouseEvent>) => {
        e.stopPropagation();
        if (clickBehavior.current.preventClick) {
            clickBehavior.current.preventClick = false;
            return;
        }

        const finalPostId = props.visibleTypes.activeFinalPosId;

        if (!(e.target instanceof HTMLDivElement) || !finalPostId) return;

        const grenadeId = e.target.dataset.grenadeId;
        if (!grenadeId) return;

        const tgPostId = props.appData.current.grenades[finalPostId][grenadeId].tg_post_id
        if (props.appData.current.platform === 'ios' || props.appData.current.platform === 'macos') {
            openLink(`https://t.me/CS2_education/${tgPostId}?`, {tryInstantView: true})
        } else {
            // openLink(`https://t.me/CS2_education/3?t=1h`, {tryBrowser: 'chrome'})
            // openInvoice(`https://t.me/CS2_education/3`)
            // shareStory(`https://t.me/CS2_education/3`, {text: 'класс'})
            openTelegramLink(`https://t.me/CS2_education/${tgPostId}`)
        }
    }, [props.visibleTypes.activeFinalPosId, props.appData])

    const handleDoubleOrSingleClickOnInitialPos = useDoubleTap(
            onDoubleTapClick,
            300,
            {onSingleTap: onSingleTapClick}
    )

    // ------------------------------------------------- Анимации ----------------------------------------------------
    const animateParams = {
        initial: {opacity: 0, scale: 0.1},
        animate: {opacity: 1, scale: 1},
        exit: {opacity: 0, scale: 0.1},
        transition: {
            duration: 0.3,
            ease: "easeInOut",
            scale: {
                type: "spring",
                stiffness: 200,
                damping: 15,
            },
        }
    }

    return (
        <motion.div
            id={"map_container"}
            className="map-container"
            {...props.themeSwitchAnimation["secondaryBgColor"]}
        >
            <TransformWrapper
                initialScale={0.95}
                minScale={0.9}
                maxScale={4}
                centerOnInit={true}
                doubleClick={{mode: 'toggle', step: 0.5, animationTime: 300, excluded: ['position-div', 'position-icon']}}
                onPanningStart={handlePanningStart}
                onPanningStop={handlePanningStop}
                wheel={{ step: 0.1 }}
                pinch={{ step: 0.1 }}
                centerZoomedOut={true}
                limitToBounds={true}
                panning={{wheelPanning: false}}
                velocityAnimation={{sensitivity: 200, animationTime: 200, equalToMove: false}}
            >
                <TransformComponent
                    wrapperStyle={{
                        width: `${mapSize}px`,
                        height: `${mapSize}px`,
                    }}
                >
                    <div
                        className="map-image-container"
                        style={{
                            backgroundImage: `url(${mapRadarImages[props.appData.current.current_map]})`,
                            width: `${mapSize}px`,
                            height: `${mapSize}px`,
                        }}
                        onClick={handleMapClick}
                    >
                        <AnimatePresence>
                            {props.visibleGrenades && !(grenadePopup) && Object.entries(props.visibleGrenades).map(([finalPosKey, grenades]) => {
                                const uniqueTypes = new Set(grenades.map((item) => item.type))

                                return (
                                    <FinalPositionComponent
                                        key={`${finalPosKey}_react_comp`}
                                        finalPosKey={finalPosKey}
                                        uniqueTypes={uniqueTypes}
                                        finalPosition={grenades[0].final_position.position}
                                        handleClickOnFinalPos={handleClickOnFinalPos}
                                        handleClickOnCircle={handleCircleClick}
                                        animateParams={animateParams}
                                    />
                                )
                            })}

                            {grenadePopup && props.visibleTypes.activeFinalPosId && (
                                <GrenadePopupContainer
                                    key={"grenade_popup_container"}
                                    themeColors={props.themeColors}
                                    finalPosKey={props.visibleTypes.activeFinalPosId}
                                    grenades={props.visibleGrenades[props.visibleTypes.activeFinalPosId]}
                                    grenadePopup={grenadePopup}
                                    handleClickOnFinalPos={handleClickOnFinalPos}
                                    animateParams={animateParams}
                                />
                                    )
                            }

                            {props.visibleTypes.activeFinalPosId && !(grenadePopup)  && props.visibleGrenades[props.visibleTypes.activeFinalPosId] &&
                                props.visibleGrenades[props.visibleTypes.activeFinalPosId].map((grenade) => (
                                    <InitialPositionComponent
                                        key={`${grenade.id}_react_comp`}
                                        grenade={grenade}
                                        handleClickOnInitialPos={handleDoubleOrSingleClickOnInitialPos}
                                        animateParams={animateParams}
                                    />
                                ))}
                        </AnimatePresence>
                    </div>
                </TransformComponent>
            </TransformWrapper>
        </motion.div>

    )
}

export default MapContainer;