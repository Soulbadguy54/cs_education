import loadImage from "../assets/other/load_image.webp";
import {FC} from "react";


const LoadOverlay: FC = () => {
    return (
        <div className="loader-overlay">
            <img
                src={loadImage}
                className="fire-animation"
                alt="Loading fire animation"
            />
        </div>
    );
};

export default LoadOverlay;