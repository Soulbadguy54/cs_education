import {getCloudStorageItem} from "@telegram-apps/sdk-react";
import {userDataServerAnswer} from "./Interfaces";


 const MAIN_URL = 'https://cs-education.ru'//   'http://192.168.1.37:8000'


export const fetchGrenadesFromDb = async (map: string | null, userId: number | undefined) => {
    let url = MAIN_URL + `/api/grenade/get_grouped?map_name=${map}`;
    if (userId) {
        url = url + `&user_id=${userId}`
    }

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            "Authorization": `Bearer ${await getCloudStorageItem('access_token')}`
        },
    })
    if (!(response.status === 200)) return {};

    return await response.json()
};


export const addOrRemoveGrenadeFromFavourite = async (userId: number, grenadeId: number, isFavourite: boolean) => {
    const headers = {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${await getCloudStorageItem('access_token')}`
    }
    if (!isFavourite) {
        await fetch(MAIN_URL + '/api/grenade/add_to_favourite', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                grenade_id: grenadeId,
                user_id: userId,
            }),
        })
    } else {
        await fetch(MAIN_URL + `/api/grenade/remove_from_favourite?grenade_id=${grenadeId}&user_id=${userId}`, {
            method: 'DELETE',
            headers: headers,
        })
    }
    return !isFavourite
};


export const checkUserInitData = async (rawData: any): Promise<userDataServerAnswer> => {
    const resp = await fetch(MAIN_URL + '/api/user/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'data': rawData})
    })
    return await resp.json()
};