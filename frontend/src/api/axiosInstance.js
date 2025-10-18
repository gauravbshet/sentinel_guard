import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001',
})

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('sg_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

api.interceptors.response.use(
    (res) => res,
    (err) => {
        if (err.response && err.response.status === 401) {
            localStorage.removeItem('sg_token')
            if (!location.pathname.includes('/login')) {
                location.href = '/login'
            }
        }
        return Promise.reject(err)
    }
)

export default api


