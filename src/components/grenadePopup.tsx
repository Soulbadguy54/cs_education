import React from "react";
import {
    Grenade, grenadeImages,
    themeColorsObject
} from "../extra/Interfaces";
import {motion} from "framer-motion";


interface GrenadePopupProps {
    themeColors: themeColorsObject,
    finalPosKey: string,
    grenades: Grenade[],
    grenadePopup: { popupPosition: string } | null,
    handleClickOnFinalPos: (e: React.MouseEvent<HTMLDivElement> | React.TouchEvent<HTMLDivElement>) => void,
    animateParams: object;
}


function GrenadePopupContainer (props: GrenadePopupProps) {
    const uniqueTypes = new Set(props.grenades.map((item) => item.type));

    return (
        <motion.div
            key={`grenade_popup_div`}
            className={"grenade-popup"}
            style={{
                height: `${5 * uniqueTypes.size + 2}%`,
                inset: props.grenadePopup?.popupPosition,
            }}
            {...props.animateParams}
            initial={{opacity: 0, scale: 0.1, transform: "translate(-50%, -50%)"}}
            animate={{opacity: 1, scale: 1, transform: "translate(-50%, -50%)"}}
            exit={{opacity: 0, scale: 0.1, transform: "translate(-50%, -50%)"}}
        >
            {props.grenades.map((item) => {
                return (
                    <motion.img
                        src={grenadeImages[item.type]}
                        key={`grenade_popup_${grenadeImages[item.type]}`}
                        alt={grenadeImages[item.type]}
                        style={{
                            width: "90%",
                            aspectRatio: 1,
                            cursor: "pointer",
                            pointerEvents: "auto",
                        }}
                        onClick={props.handleClickOnFinalPos}
                        {...props.animateParams}
                        data-position-key={props.finalPosKey}
                        data-extra-key={item.type}
                    />
                )
            })}
        </motion.div>
    );
}


export default GrenadePopupContainer;
