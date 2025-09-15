import mirageRadarImg from '../assets/map_radars/mirage.webp';
import anubisRadarImg from '../assets/map_radars/anubis.webp';
import ancientRadarImg from '../assets/map_radars/ancient.webp';
import dust2RadarImg from '../assets/map_radars/dust2.webp';
import trainRadarImg from '../assets/map_radars/train.webp';
import infernoRadarImg from '../assets/map_radars/inferno.webp';
import overpassRadarImg from '../assets/map_radars/overpass.webp';
import smokeIcon from '../assets/grenade_icons/smoke_cloud.webp';
import molotovIcon from '../assets/grenade_icons/fire.webp';
import heIcon from '../assets/grenade_icons/explosion_v2.webp';
import flashIcon from '../assets/grenade_icons/flashlight_v2.webp';
import smokeFilterIcon from '../assets/grenade_icons/smoke.webp';
import molotovFilterIcon from '../assets/grenade_icons/molotov.webp';
import heFilterIcon from '../assets/grenade_icons/he.webp';
import flashFilterIcon from '../assets/grenade_icons/flash.webp';
import ctFilterIcon from '../assets/side_icons/ct.webp';
import tFilterIcon from '../assets/side_icons/t.webp';
import easyDot from "../assets/marks/easy.webp";
import mediumDot from "../assets/marks/medium.webp";
import hardDot from "../assets/marks/hard.webp";
import likedEasyDot from '../assets/marks/liked_easy.webp'
import likedMediumDot from '../assets/marks/liked_medium.webp'
import likedHardDot from '../assets/marks/liked_hard.webp'
import easyDifImg from '../assets/difficulty/easy.webp';
import mediumDifImg from '../assets/difficulty/medium.webp';
import hardDifImg from '../assets/difficulty/hard.webp';
import instructionImgS1Ru from '../assets/other/intruction_s1_ru.webp'
import instructionImgS2Ru from '../assets/other/intruction_s2_ru.webp'
import instructionImgS1Eng from '../assets/other/intruction_s1_eng.webp'
import instructionImgS2Eng from '../assets/other/intruction_s2_eng.webp'
import {grenadeSides, grenadeTypes, maps, themes} from "./enums";
import mirageIcon from '../assets/map_icons/mirage.webp';
import anubisIcon from '../assets/map_icons/anubis.webp';
import dust2Icon from '../assets/map_icons/dust2.webp';
import nukeIcon from '../assets/map_icons/nuke.webp';
import trainIcon from '../assets/map_icons/train.webp';
import infernoIcon from '../assets/map_icons/inferno.webp';
import ancientIcon from '../assets/map_icons/ancient.webp';
// import vertigoIcon from '../assets/map_icons/vertigo.webp';
import overpassIcon from '../assets/map_icons/overpass.webp';
import {User} from "@telegram-apps/sdk-react";


export const mapIcons = {
    [maps.MIRAGE]: mirageIcon,
    [maps.DUST2]: dust2Icon,
    [maps.INFERNO]: infernoIcon,
    [maps.ANUBIS]: anubisIcon,
    [maps.TRAIN]: trainIcon,
    [maps.ANCIENT]: ancientIcon,
    // [maps.VERTIGO]: vertigoIcon,
    [maps.NUKE]: nukeIcon,
    [maps.OVERPASS]: overpassIcon,
}

export const mapRadarImages = {
    [maps.MIRAGE]: mirageRadarImg,
    [maps.DUST2]: dust2RadarImg,
    [maps.INFERNO]: infernoRadarImg,
    [maps.ANUBIS]: anubisRadarImg,
    [maps.TRAIN]: trainRadarImg,
    [maps.ANCIENT]: ancientRadarImg,
    [maps.OVERPASS]: overpassRadarImg,
    // [maps.VERTIGO]: vertigoRadarImg,
};

export const filterImages = {
    [grenadeTypes.SMOKE]: smokeFilterIcon,
    [grenadeTypes.HE]: heFilterIcon,
    [grenadeTypes.MOLOTOV]: molotovFilterIcon,
    [grenadeTypes.FLASH]: flashFilterIcon,
    [grenadeSides.CT]: ctFilterIcon,
    [grenadeSides.T]: tFilterIcon,
}

export const grenadeImages = {
    [grenadeTypes.SMOKE]: smokeIcon,
    [grenadeTypes.HE]: heIcon,
    [grenadeTypes.MOLOTOV]: molotovIcon,
    [grenadeTypes.FLASH]: flashIcon,
}

export const dotImages = {
    1: easyDot,
    2: mediumDot,
    3: hardDot,
}

export const likedDotImages = {
    1: likedEasyDot,
    2: likedMediumDot,
    3: likedHardDot,
}

export const difficultImages = {
    1: easyDifImg,
    2: mediumDifImg,
    3: hardDifImg,
}

export const instructionImages = {
    ru: {1: instructionImgS1Ru, 2: instructionImgS2Ru},
    eng: {1: instructionImgS1Eng, 2: instructionImgS2Eng},
}

export const textData = {
    ru: {
        diff: {
            header: 'Переключатель сложности',
            text: 'Выбирай уровень сложности сетапов',
        },
        theme: 'Смена темы',
        filters: {
            header: 'Панель фильтров',
            text: 'Быстрее находи нужные гранаты',
        },
        subscribe: {
            header: 'Не видим подписочки!',
            text: 'Для корректной работы приложения подпишись на наш любимый канал.',
            text2: 'Приложение закроется, не пугайся!',
        }
    },
    eng: {
        diff: {
            header: 'Difficulty switcher',
            text: 'Choose the difficulty level of setups',
        },
        theme: 'Changing theme',
        filters: {
            header: 'Filter panel',
            text: 'Find the grenades faster',
        },
        subscribe: {
            header: 'You are not subscribed!',
            text: 'For the app to work as intended, you need to subscribe to our cozy channel!',
            text2: "App will be closed, it's OK!",
        }
    },
}

export interface filterTypes {
    type: {
        [grenadeTypes.SMOKE]: boolean,
        [grenadeTypes.MOLOTOV]: boolean,
        [grenadeTypes.HE]: boolean,
        [grenadeTypes.FLASH]: boolean,
    },
    side: {
        [grenadeSides.CT]: boolean,
        [grenadeSides.T]: boolean,
    },
    is_favourite: boolean,
    difficulty: number,
    activeFinalPosId: null | string,
    extraFilter: null | undefined | grenadeTypes | string,
}

export interface appDataI {
    grenades: { [key: string]: {[key: string]: Grenade} },
    current_map: maps | string,
    userDataFromTg: User | undefined,
    info_clicked: boolean,
    access_token: string,
    platform: string,
}

export interface actionsI {
    themeChanging: boolean,
}

export interface activeOverlays {
    loading: boolean,
    info: boolean,
    homeScreen: boolean,
    channel_subscribe: boolean,
}

export interface Position {
    id: number;
    name: string;
    position: {
        left: number;
        right: number;
        top: number;
        bottom: number;
    }
}

export interface Grenade {
  id: number,
  side: grenadeSides;
  difficult: number;
  type: grenadeTypes;
  is_favourite: boolean,
  final_position: Position;
  initial_position: Position;
  tg_post_id: number;
  data: {
    is_insta: boolean;
  };
  tg_data: {
    likes: number;
    dislikes: number;
  };
}

export interface gridElementParamsI {
    tileSize: number,
    gapSize: number,
    paddingSize: number
}

export interface themeColorsObject {
    bgColor: string,
    secondaryBgColor: string,
    textColor: string,
    contrastColor: string,
    headerColor: `#${string}`,
    type: string,
}

export const appColors: {[key: string]: themeColorsObject} = {
    [themes.DARK]: {
        bgColor: '#333333',
        secondaryBgColor: '#1f1f1f',
        textColor: '#ffffff',
        contrastColor: '#a1a1a1',
        headerColor: '#e58626',
        type: themes.DARK
    },
    [themes.LIGHT]: {
        bgColor: '#e5b27e',
        secondaryBgColor: '#92765a',
        textColor: '#fffcf8',
        contrastColor: '#fffcf8',
        headerColor: '#e58626',
        type: themes.LIGHT
    },
}

export const currentTheme: {type: null | string} = {type: null};

export interface appSizeI {
    height: number,
    width: number,
}

export interface clickBehaviorI {
    cursorPos: {x: number, y: number},
    preventClick: boolean,
}

export interface userDataServerAnswer {
    access_token: string,
    token_type: string,
    is_subscribed: boolean,
}