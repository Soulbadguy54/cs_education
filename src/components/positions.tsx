import React, {memo} from "react";
import {dotImages, likedDotImages, Grenade, grenadeImages} from "../extra/Interfaces";
import circle from "../assets/other/circle.webp";
import {motion} from "framer-motion";
import {grenadeTypes} from "../extra/enums";
import {CallbackFunction} from "use-double-tap";


interface initialPositionProps {
    grenade: Grenade;
    handleClickOnInitialPos: { onClick: CallbackFunction<Element>; },
    animateParams: object;
}

interface finalPositionProps {
    finalPosKey: string,
    uniqueTypes: Set<grenadeTypes>,
    finalPosition: {left: number, right: number , bottom: number, top: number},
    handleClickOnFinalPos: (e: React.MouseEvent<HTMLDivElement> | React.TouchEvent<HTMLDivElement>) => void,
    handleClickOnCircle: (e: React.MouseEvent<HTMLDivElement> | React.TouchEvent<HTMLDivElement>) => void,
    animateParams: object,
}


export const InitialPositionComponent = memo((props: initialPositionProps) => {
    const dotIconSrc = props.grenade.is_favourite ? likedDotImages[props.grenade.difficult] : dotImages[props.grenade.difficult];
    const initial_position = props.grenade.initial_position.position;

    return (
        <motion.div
            className={"position-div"}
            key={`initial_${props.grenade.id}`}
            initial={{pointerEvents: "auto"}}
            animate={{pointerEvents: "auto"}}
            exit={{pointerEvents: "none"}}
            style={{
                left: `${initial_position.left}%`,
                right: `${initial_position.right}%`,
                bottom: `${initial_position.bottom}%`,
                top: `${initial_position.top}%`,
                width: "5%",
                transform: "translate(-50%, -100%)",
            }}
            data-grenade-id={props.grenade.id}
            {...props.handleClickOnInitialPos}
        >
            <motion.img
                src={dotIconSrc}
                className={"position-icon"}
                key={`initial_${props.grenade.id}_img`}
                {...props.animateParams}
            />
        </motion.div>
    );
    },
    (prevProps, nextProps) => {
    return (
            prevProps.grenade.id === nextProps.grenade.id &&
            prevProps.grenade.is_favourite === nextProps.grenade.is_favourite &&
            prevProps.grenade.difficult === nextProps.grenade.difficult
        )
}
);

export const FinalPositionComponent = memo((props: finalPositionProps) => {
    const [grenadeType] = props.uniqueTypes
    let iconSrc = grenadeImages[grenadeType];
    let onClickFunction = props.handleClickOnFinalPos;
    let elemKey = `final_${props.finalPosKey}_${grenadeType}`;

    if (props.uniqueTypes.size > 1) {
        iconSrc = circle;
        onClickFunction = props.handleClickOnCircle;
        elemKey = `final_${props.finalPosKey}_circle`;
    }
    return (
        <motion.div
            className="position-div"
            onClick={onClickFunction}
            key={elemKey}
            initial={{pointerEvents: "auto"}}
            animate={{pointerEvents: "auto"}}
            exit={{pointerEvents: "none"}}
            style={{
                left: `${props.finalPosition.left}%`,
                right: `${props.finalPosition.right}%`,
                bottom: `${props.finalPosition.bottom}%`,
                top: `${props.finalPosition.top}%`,
                width: "5%",
                transform: "translate(-50%, -50%)",

            }}
            data-position-key={props.finalPosKey}
        >
            <motion.img
                className="position-icon"
                src={iconSrc}
                key={`final_${props.finalPosKey}_img`}
                {...props.animateParams}
            />
            {props.uniqueTypes.size > 1 && (
                <motion.span
                    className={"circle-span"}
                    {...props.animateParams}
                >
                    {props.uniqueTypes.size}
                </motion.span>
            )}
        </motion.div>
    );
    },
    (prevProps, nextProps) => {
        return (
            prevProps.finalPosKey === nextProps.finalPosKey &&
            prevProps.uniqueTypes === nextProps.uniqueTypes
        )
}
);