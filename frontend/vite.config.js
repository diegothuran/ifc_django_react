import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  build: {
    // Compilar para o diretório static do Django
    outDir: '../static/dist',
    emptyOutDir: true,
    
    // Gerar manifest para Django saber quais arquivos carregar
    manifest: true,
    
    rollupOptions: {
      input: {
        // Pontos de entrada para diferentes páginas
        dashboard: path.resolve(__dirname, 'src/dashboard.js'),
        viewer: path.resolve(__dirname, 'src/viewer.js'),
        notifications: path.resolve(__dirname, 'src/notifications.js'),
        search: path.resolve(__dirname, 'src/search.js'),
      },
      output: {
        // Nomes de arquivo consistentes
        entryFileNames: 'js/[name].[hash].js',
        chunkFileNames: 'js/[name].[hash].js',
        assetFileNames: '[ext]/[name].[hash].[ext]',
      },
    },
  },
  
  server: {
    // Porta para desenvolvimento
    port: 3000,
    
    // Proxy para API do Django durante desenvolvimento
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})

