import { motion } from 'framer-motion';
import {activeOverlays, appDataI, difficultImages, filterTypes, themeColorsObject} from "../extra/Interfaces";
import {Dispatch, FC, RefObject, SetStateAction} from "react";


interface SwitchProps {
    visibleTypes: filterTypes,
    setVisibleTypes:  Dispatch<SetStateAction<filterTypes>>,
    themeColors: themeColorsObject,
    appData: RefObject<appDataI>,
    overlay: activeOverlays,
    setOverlay: Dispatch<SetStateAction<activeOverlays>>,
    themeSwitchAnimation: object,
}

const SwitchContainer: FC<SwitchProps> = (props: SwitchProps) => {
    const currentDifficulty: string = props.visibleTypes.difficulty.toString()

    return (
        <motion.div id="switch-track" className="switch-track" {...props.themeSwitchAnimation["BgColor"]}>
            {Object.entries(difficultImages).map(([difNum, difIcon]) => (
                <motion.div
                    key={`${difNum}_dif`}
                    className={`switch-position ${currentDifficulty === difNum ? 'active' : ''}`}
                    {...props.themeSwitchAnimation["secondaryBgColor"]}
                    onClick={() => {
                        if (props.overlay.info) {
                            props.setOverlay((prev) => ({...prev, info: false}))
                            return
                        }
                        props.setVisibleTypes({...props.visibleTypes, difficulty: parseInt(difNum), activeFinalPosId: null });
                    }}
                >
                    <motion.img
                        src={difIcon}
                        className="switch-icon"
                        initial={false}
                        animate={{
                            opacity: difNum === currentDifficulty ? 1 : 0.1,
                            scale: [1.2, 1],
                            transition: {
                                duration: 0.3,
                                ease: "easeInOut",
                            }
                        }}
                        whileTap={{
                            scale: 1.1,
                            transition: {
                                duration: 0.1,
                                ease: "easeIn"
                            }
                        }}
                    />
                </motion.div>
            ))}
        </motion.div>
    );
};

export default SwitchContainer;