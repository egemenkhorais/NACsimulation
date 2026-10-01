import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
});

export const loginDevice = async (username, password, macAddress) => {
    const response = await api.post('/auth/login', {
        username: username,
        password: password,
        mac_address: macAddress,
        switch_port: "GigabitEthernet0/1"
    });
    return response.data;
};

export const quarantinePort = async (macAddress, interfaceName) => {
    const response = await api.post('/network/quarantine', {
        mac_address: macAddress,
        interface: interfaceName
    });
    return response.data;
};

export const getDevices = async () => {
    const response = await api.get('/network/devices');
    return response.data;
};

export const getLogs = async () => {
    const response = await api.get('/network/logs');
    return response.data;
};