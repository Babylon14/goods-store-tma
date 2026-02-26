import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [products, setProducts] = useState([])

  // ЗАМЕНИ ЭТУ ПЕРЕМЕННУЮ на твою ссылку бэкенда (порт 8000)
  const API_URL = "https://precerebroid-unpromotional-stefanie.ngrok-free.dev"; 

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready()
    }

    // 2. Запрашиваем товары у бэкенда по НОВОЙ ССЫЛКЕ
    fetch(`${API_URL}/api/v1/products/`, {
      headers: {
        // Этот заголовок убирает страницу-предупреждение ngrok
        'ngrok-skip-browser-warning': 'true'
      }
    }) 
      .then(res => res.json())
      .then(data => {
        console.log("Получили товары:", data)
        setProducts(data)
      })
      .catch(err => console.error("Ошибка загрузки:", err))
  }, [])

  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h1>Магазин TMA 🛍️</h1>
      <div style={{ display: 'grid', gap: '20px' }}>
        {products.length === 0 && <p>Загрузка товаров...</p>}
        {products.map(product => (
          <div key={product.id} style={{ border: '1px solid #ccc', borderRadius: '10px', padding: '10px' }}>
            {/* Картинка теперь тоже берется по НОВОЙ ССЫЛКЕ */}
            <img 
              src={`${API_URL}${product.image_url}`} 
              alt={product.title} 
              style={{ width: '100%', borderRadius: '8px' }} 
            />
            <h3>{product.title}</h3>
            <p>{product.description}</p>
            <button style={{ width: '100%', padding: '10px', backgroundColor: '#0088cc', color: 'white', border: 'none', borderRadius: '5px' }}>
              Купить
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App

