const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
    getSchools: () => ipcRenderer.invoke('get-schools'),
    startVerify: (data) => ipcRenderer.invoke('start-verify', data),
    onLogUpdate: (callback) => ipcRenderer.on('log-update', (event, msg) => callback(msg)),
    selectFile: () => ipcRenderer.invoke('select-file'),
    selectFolder: () => ipcRenderer.invoke('select-folder'),
    generateDocs: (data) => ipcRenderer.invoke('generate-docs', data),
    getConfig: () => ipcRenderer.invoke('get-config'),
    setConfig: (config) => ipcRenderer.invoke('set-config', config)
});
