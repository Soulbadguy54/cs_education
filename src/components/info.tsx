import {activeOverlays, appSizeI, instructionImages, textData, themeColorsObject} from "../extra/Interfaces";
import {motion} from "framer-motion";
import '../styles/main.css'

interface InfoProps {
    overlay: activeOverlays,
    setOverlay: React.Dispatch<React.SetStateAction<activeOverlays>>
    themeColors: themeColorsObject,
    stablePageSize: appSizeI,
    userLanguage: string,
}

const InfoOverlay: React.FC<InfoProps> = (props: InfoProps) => {
    const PX_OFFSET = 5
    const [DEFAULT_LINE_SIZE, GAP_BEFORE_TEXT] = [5, 1]

    const getPositionOfElementById = (id: string) => {
        return document.getElementById(id)?.getBoundingClientRect() || {bottom: 0, top: 0, left: 0, right: 0, height: 0, width: 0}

    }
    const filterContainerPosition = getPositionOfElementById("controls-container")
    const filterFavouritePosition = getPositionOfElementById("favourite_filter")
    const diffFilterPosition = getPositionOfElementById("switch-track")
    const themeContainerPosition = getPositionOfElementById("theme-icon")
    const mapContainerPosition = getPositionOfElementById("map_container")

    const bottomFilterBorderParams = {
        height: filterFavouritePosition.bottom - filterContainerPosition.top + PX_OFFSET * 1.5,
        width: filterContainerPosition.width - 8 * PX_OFFSET
    };
    const diffFilterBorderParams = {height: diffFilterPosition.height + 2 * PX_OFFSET, width: diffFilterPosition.width + 2 * PX_OFFSET}

    const instructionImgHeight =  props.stablePageSize.width / 2.6


    const borderVariants = {
        visible: { strokeDashoffset: 0, transition: { duration: 1, ease: "easeInOut" } },
    };

    const lineAnimation = { duration: 0.5, delay: 1, ease: "easeInOut" }
    const imageAnimation = {duration: 0.5, delay: 1.25}

    const textVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { duration: 0.5, delay: 1 } },
    };

    const userLang = props.userLanguage == 'ru'? 'ru' : 'eng'

    return (
        <motion.div
            className="blur-overlay"
            initial={{opacity: 0}}
            animate={{opacity: 1}}
            exit={{opacity: 0}}
            transition={{duration: 0.3}}
            onClick={() => props.setOverlay((prev) => ({...prev, info: false}))} // Закрытие при клике на оверлей
        >
            {filterContainerPosition && filterFavouritePosition &&
                (<motion.div
                    key={"filterContainerBoarder"}
                    className="border-in-overlay"
                    style={{
                        top: filterContainerPosition.top,
                        left: filterContainerPosition.left + PX_OFFSET * 4,
                        right: filterContainerPosition.right - PX_OFFSET * 4,
                        bottom: filterFavouritePosition.bottom + PX_OFFSET * 1.5,
                        width: bottomFilterBorderParams.width,
                        height: bottomFilterBorderParams.height,
                    }}
                >
                    <svg
                        width="100%"
                        height="100%"
                        style={{position: "absolute", top: 0, left: 0}}
                        preserveAspectRatio="none"
                    >
                        <motion.rect
                            x="0"
                            y="0"
                            rx="10" // Радиус скругления углов (в пикселях)
                            ry="10"
                            width="100%"
                            height="100%"
                            fill="none"
                            stroke={props.themeColors.contrastColor}
                            strokeWidth={props.stablePageSize.width * 0.005}
                            strokeDasharray={bottomFilterBorderParams.width * 2 + bottomFilterBorderParams.height * 2}
                            variants={borderVariants}
                            initial={{strokeDashoffset: bottomFilterBorderParams.width * 2 + bottomFilterBorderParams.height * 2}}
                            animate="visible"
                        />
                    </svg>
                    <motion.div
                        className="line"
                        style={{
                            transformOrigin: "bottom",
                            top: `-${DEFAULT_LINE_SIZE}vw`,
                            height: `${DEFAULT_LINE_SIZE}vw`,
                            width: props.stablePageSize.width * 0.005,
                            background: props.themeColors.contrastColor,
                        }}
                        initial={{scaleY: 0, originY: 1}}
                        animate={{
                            scaleY: 1,
                            originY: 1,
                            transition: lineAnimation
                    }}
                    />
                    <motion.div
                        className="overlay-text"
                        style={{
                            top: `-${DEFAULT_LINE_SIZE + GAP_BEFORE_TEXT}vw`,
                            transform: "translateX(-50%) translateY(-100%)",
                            color: props.themeColors.textColor,
                        }}
                        variants={textVariants}
                        initial="hidden"
                        animate="visible"
                    >
                        <span className={"large-font"}><strong>{textData[userLang].filters.header}</strong></span>
                        <br/>
                        <span className={"little-font"}>{textData[userLang].filters.text}</span>
                    </motion.div>
                </motion.div>)}

            {diffFilterPosition &&
                (<motion.div
                    key={"diffFilterBoarder"}
                    className="border-in-overlay"
                    style={{
                        top: diffFilterPosition.top - PX_OFFSET,
                        left: diffFilterPosition.left - PX_OFFSET,
                        right: diffFilterPosition.right + PX_OFFSET,
                        bottom: diffFilterPosition.bottom + PX_OFFSET,
                        width: diffFilterBorderParams.width,
                        height: diffFilterBorderParams.height,
                    }}
                >
                    <svg
                        width="100%"
                        height="100%"
                        style={{position: "absolute", top: 0, left: 0}}
                        preserveAspectRatio="none"
                    >
                        <motion.rect
                            x="0"
                            y="0"
                            rx="10"
                            ry="10"
                            width="100%"
                            height="100%"
                            fill="none"
                            stroke={props.themeColors.contrastColor}
                            strokeWidth={props.stablePageSize.width * 0.005}
                            strokeDasharray={diffFilterBorderParams.width * 2 + diffFilterBorderParams.height * 2}
                            variants={borderVariants}
                            initial={{strokeDashoffset: diffFilterBorderParams.width * 2 + diffFilterBorderParams.height * 2}}
                            animate="visible"
                        />
                    </svg>
                    <motion.div
                        className="line"
                        style={{
                            transformOrigin: "top",
                            bottom: `-${DEFAULT_LINE_SIZE}vw`,
                            height: `${DEFAULT_LINE_SIZE}vw`,
                            width: props.stablePageSize.width * 0.005,
                            background: props.themeColors.contrastColor,
                        }}
                        initial={{ scaleY: 0, originY: 0 }}
                        animate={{
                            scaleY: 1,
                            originY: 0,
                            transition: lineAnimation
                        }}
                    />
                    <motion.div
                        className="overlay-text"
                        style={{
                            bottom: `-${DEFAULT_LINE_SIZE + GAP_BEFORE_TEXT}vw`,
                            transform: "translateX(-50%) translateY(100%)",
                            color: props.themeColors.textColor,
                        }}
                        variants={textVariants}
                        initial="hidden"
                        animate="visible"
                    >
                        <span className="large-font">
                          <strong>{textData[userLang].diff.header}</strong>
                        </span>
                        <br/>
                        <span className="little-font">{textData[userLang].diff.text}</span>
                    </motion.div>
                </motion.div>)}
            {themeContainerPosition &&
                (<motion.div
                    key={"ThemeIconDiv"}
                    className="border-in-overlay"
                    style={{
                        top: themeContainerPosition.top,
                        left: themeContainerPosition.left,
                        right: themeContainerPosition.right,
                        bottom: themeContainerPosition.bottom,
                        height: themeContainerPosition.height,
                        width: themeContainerPosition.width,
                    }}
                    >
                    <motion.div
                        className="line"
                        style={{
                            transformOrigin: "top",
                            bottom: `-${DEFAULT_LINE_SIZE * 4.2}vw`,
                            width: props.stablePageSize.width * 0.005,
                            height: `${DEFAULT_LINE_SIZE * 3.8}vw`,
                            background: props.themeColors.contrastColor,
                        }}
                        initial={{scaleY: 0, originY: 0}}
                        animate={{
                            scaleY: 1,
                            originY: 0,
                            transition: lineAnimation
                        }}
                    />
                        <motion.div
                            className="overlay-text"
                            style={{
                                bottom: `-${DEFAULT_LINE_SIZE * 4.2 + GAP_BEFORE_TEXT}vw`,
                                transform: "translateX(-90%) translateY(100%)",
                                color: props.themeColors.textColor,
                            }}
                            variants={textVariants}
                            initial="hidden"
                            animate="visible"
                        >
                            <span className="large-font"><strong>{textData[userLang].theme}</strong></span>
                        </motion.div>
                    </motion.div>
                )}
            <motion.div
                key={"instruction_block"}
                className={"instruction-block"}
                style={{
                    top: mapContainerPosition.top + mapContainerPosition.height / 2 - instructionImgHeight / 2,
                    left: 0,
                    right: props.stablePageSize.width,
                    bottom: mapContainerPosition.bottom - mapContainerPosition.height / 2 + instructionImgHeight / 2,
                    width: props.stablePageSize.width,
                    height: instructionImgHeight,
                }}
                initial={{opacity: 0}}
                animate={{opacity: 1}}
                transition={imageAnimation}

            >
                {Object.entries(instructionImages[userLang]).map(([index, img]) => {
                    return (
                        <img
                            src={img}
                            key={`instructionImages_${index}`}
                            style={{
                                width: instructionImgHeight,
                                height: instructionImgHeight,
                                border: `${props.themeColors.contrastColor} solid ${props.stablePageSize.width * 0.005}px`,
                            }}
                        />
                    )})
                }
            </motion.div>
        </motion.div>
    );
};

export default InfoOverlay;