import '../styles/menu.css';
import {FC} from "react";

const TelegramRequiredComponent: FC = () => {
    return (
        <div className="error-container">
            <h1>Доступно только через Telegram Mini App</h1>
            <p>Пожалуйста, откройте приложение через Telegram Mini App.</p>
            <a href="https://t.me/CS2_education">Открыть в Telegram</a>
        </div>
    );
};

export default TelegramRequiredComponent;