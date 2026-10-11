import {defineConfig} from 'vite';
import {VitePWA} from 'vite-plugin-pwa';
export default defineConfig({plugins:[VitePWA({registerType:'autoUpdate',manifest:{name:'Trail Whisperer',short_name:'Trail',theme_color:'#101c18',background_color:'#101c18',display:'standalone',icons:[{src:'/icon.svg',sizes:'any',type:'image/svg+xml',purpose:'any'}]},workbox:{globPatterns:['**/*.{js,css,html,svg}'],navigateFallbackDenylist:[/^\/api/,/^\/media/],runtimeCaching:[]}})],server:{proxy:{'/api':'http://127.0.0.1:8000','/media':'http://127.0.0.1:8000'}}});
