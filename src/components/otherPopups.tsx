import React from "react";
import {textData, themeColorsObject} from "../extra/Interfaces";
import {openTelegramLink} from "@telegram-apps/sdk";
import { motion } from "framer-motion";
import {miniApp} from "@telegram-apps/sdk-react";


interface SubscribePopupProps {
    themeColors: themeColorsObject,
    userLanguage: string,
}

function SubscribePopup(props: SubscribePopupProps) {
    return (
        <motion.div
            className="subscribe-overlay"
            initial={{opacity: 0}}
            animate={{opacity: 1}}
            exit={{opacity: 0}}
            transition={{duration: 0.3}}
        >
            <div
                className="subscribe-popup"
                style={{
                    backgroundColor: props.themeColors.secondaryBgColor,
                    border: `2px solid ${props.themeColors.headerColor}`,
                    borderRadius: 6,
                    color: props.themeColors.textColor,
                    gap: "4%",
                }}
            >
                <div
                    style={{
                        textAlign: "center",
                        flexGrow: 1,
                    }}
                >
                    <span
                        className={"large-font"}><strong>{textData[props.userLanguage].subscribe.header}</strong></span>
                </div>
                <div
                    style={{
                        textAlign: "justify",
                        flexGrow: 1,
                    }}
                >
                    <span className={"little-font"}>{textData[props.userLanguage].subscribe.text}</span>
                    <br/>
                    <span className={"little-font"}><strong>{textData[props.userLanguage].subscribe.text2}</strong></span>
                </div>
                <motion.div
                    className={"subscribe-button"}
                    onClick={() => {
                        openTelegramLink("https://t.me/CS2_education")
                        miniApp.close.ifAvailable()
                    }}
                    whileTap={{scale: 0.9}}
                    whileHover={{border: `2px solid ${props.themeColors.headerColor}`,}}
                    style={{
                        backgroundColor: props.themeColors.bgColor,
                        border: `2px solid ${props.themeColors.contrastColor}`,
                        color: props.themeColors.headerColor,
                    }}

                >
                    <span className={"large-font"}><strong>@CS2_education</strong></span>
                </motion.div>
            </div>
        </motion.div>
    );
}


export default SubscribePopup;