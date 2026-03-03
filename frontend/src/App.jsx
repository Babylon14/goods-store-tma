import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [products, setProducts] = useState([])
  const [cart, setCart] = useState({})
  const [screen, setScreen] = useState('main') // 'main' или 'cart'
  
  const tg = window.Telegram?.WebApp;
  const API_URL = window.location.origin;

  // 1. Первичная загрузка и настройка TG
  useEffect(() => {
    if (tg) {
      tg.ready();
      tg.expand();
      // Настраиваем BackButton сразу
      tg.BackButton.onClick(() => setScreen('main'));
    }

    fetch(`${API_URL}/api/v1/products/`, {
      headers: { 'ngrok-skip-browser-warning': 'true' }
    }) 
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => console.error("Ошибка загрузки:", err))
  }, [])

  // 2. Расчет общей суммы заказа
  const totalPrice = Object.keys(cart).reduce((sum, id) => {
    const product = products.find(p => p.id === parseInt(id));
    const price = product?.variants?.[0]?.price || 0;
    return sum + (price * cart[id]);
  }, 0);

  // 3. Управление кнопками Telegram (MainButton и BackButton)
  useEffect(() => {
    if (!tg) return;

    if (screen === 'main') {
      tg.BackButton.hide();
      if (totalPrice > 0) {
        tg.MainButton.setParams({
          text: `ПОСМОТРЕТЬ ЗАКАЗ (${totalPrice} ₽)`,
          color: '#2481cc',
          is_visible: true
        });
      } else {
        tg.MainButton.hide();
      }
    } else {
      tg.BackButton.show();
      tg.MainButton.setParams({
        text: `ОФОРМИТЬ ЗАКАЗ`,
        color: '#31b545', // Зеленая кнопка для финального шага
        is_visible: true
      });
    }
  }, [totalPrice, screen]);

  // 4. Обработка клика по главной кнопке
  useEffect(() => {
    const handleMainButton = () => {
      if (screen === 'main') {
        setScreen('cart');
      } else {
        tg.showConfirm(`Подтвердить заказ на сумму ${totalPrice} ₽?`, (ok) => {
          if (ok) {
            tg.sendData(JSON.stringify({
              items: cart,
              totalPrice: totalPrice
            }));
          }
        });
      }
    };
    tg?.onEvent('mainButtonClicked', handleMainButton);
    return () => tg?.offEvent('mainButtonClicked', handleMainButton);
  }, [totalPrice, screen, cart]);

  // 5. Функции изменения количества в корзине
  const toggleCart = (id, delta) => {
    setCart(prev => {
      const newQty = (prev[id] || 0) + delta;
      const newCart = { ...prev };
      if (newQty <= 0) delete newCart[id];
      else newCart[id] = newQty;
      return newCart;
    });
    tg?.HapticFeedback.impactOccurred('light');
  };

  // --- РЕНДЕРИНГ ЭКРАНА КОРЗИНЫ ---
  if (screen === 'cart') {
    const cartItems = Object.keys(cart).map(id => {
      const product = products.find(p => p.id === parseInt(id));
      return { ...product, count: cart[id] };
    });

    return (
      <div className="cart-container" style={{ padding: '20px', paddingBottom: '100px', minHeight: '100vh' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '25px' }}>Ваш заказ 🛒</h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {cartItems.map(item => (
            <div key={item.id} style={{ 
              display: 'flex', 
              alignItems: 'center', 
              background: 'var(--tg-theme-secondary-bg-color, #2c2c2e)',
              padding: '12px',
              borderRadius: '16px'
            }}>
              <img src={`${API_URL}${item.image_url}`} style={{ width: '64px', height: '64px', borderRadius: '12px', objectFit: 'cover', marginRight: '15px' }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: '600', fontSize: '15px' }}>{item.title}</div>
                <div style={{ fontSize: '15px', opacity: 0.7 }}>{item.variants?.[0]?.price} ₽ × {item.count}</div>
              </div>
              <div style={{ fontWeight: 'bold', color: 'var(--tg-theme-link-color)' }}>
                {item.variants?.[0]?.price * item.count} ₽
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: '30px', padding: '20px', background: 'rgba(255,255,255,0.05)', borderRadius: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Итого:</span>
            <span style={{ fontSize: '22px', fontWeight: '800' }}>{totalPrice} ₽</span>
          </div>
        </div>
      </div>
    );
  }

  // --- РЕНДЕРИНГ ГЛАВНОГО ЭКРАНА (ВИТРИНА) ---
  return (
    <div className="store-container" style={{ padding: '5px', paddingBottom: '100px' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Магазин товаров ручной работы🛍️</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
        {products.length === 0 && <p style={{ gridColumn: '1/-1', textAlign: 'center' }}>Загрузка товаров...</p>}
        {products.map(product => (
          <div key={product.id} style={{ 
            background: 'var(--tg-theme-secondary-bg-color, #2c2c2e)', 
            borderRadius: '16px', 
            padding: '10px',
            display: 'flex', flexDirection: 'column'
          }}>
            <img 
              src={`${API_URL}${product.image_url}`} 
              alt={product.title}
              onClick={() => {
                setSelectedImage(`${API_URL}${product.image_url}`);
                tg?.HapticFeedback.impactOccurred('medium'); // Вибрация при открытии
              }}
              style={{ 
                width: '100%', 
                borderRadius: '10px', 
                aspectRatio: '1/1', 
                objectFit: 'cover',
                cursor: 'zoom-in' // Курсор-лупа
              }} 
            />
            <h3 style={{ fontSize: '17px', margin: '10px 0 5px 0', minHeight: '34px' }}>{product.title}</h3>
            <p style={{ fontSize: '14px', opacity: 0.7, marginBottom: '8px' }}>{product.description}</p>
            <p style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '12px', color: 'var(--tg-theme-link-color)' }}>
                {product.variants?.[0]?.price} ₽
            </p>
            
            <div style={{ marginTop: 'auto' }}>
                {cart[product.id] ? (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <button onClick={() => toggleCart(product.id, -1)} className="btn-counter">-</button>
                    <span style={{ fontWeight: 'bold' }}>{cart[product.id]}</span>
                    <button onClick={() => toggleCart(product.id, 1)} className="btn-counter">+</button>
                  </div>
                ) : (
                  <button onClick={() => toggleCart(product.id, 1)} className="btn-buy">Купить</button>
                )}
            </div>
          </div>
        ))}
      </div>
    {/* МОДАЛЬНОЕ ОКНО ДЛЯ УВЕЛИЧЕНИЯ КАРТИНКИ */}
{selectedImage && (
  <div 
    onClick={() => setSelectedImage(null)} // Закрыть при клике в любое место
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0,0,0,0.9)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      animation: 'fadeIn 0.2s ease'
    }}
  >
    <img 
      src={selectedImage} 
      style={{ 
        maxWidth: '95%', 
        maxHeight: '80%', 
        borderRadius: '15px',
        boxShadow: '0 0 20px rgba(255,255,255,0.1)' 
      }} 
    />
    <div style={{
      position: 'absolute',
      top: '20px',
      right: '20px',
      color: 'white',
      fontSize: '30px',
      fontWeight: 'bold'
    }}>×</div>
  </div>
)}
    </div>
  )
}

// Простые стили для кнопок (можно добавить в App.css)
const btnStyle = {
  border: 'none', borderRadius: '10px', fontWeight: 'bold', cursor: 'pointer'
};

// Вспомогательные стили внутри JS для простоты копирования
const buyBtnStyle = { ...btnStyle, width: '100%', padding: '10px', backgroundColor: 'var(--tg-theme-button-color)', color: 'white' };
const counterBtnStyle = { ...btnStyle, width: '38px', height: '38px', backgroundColor: 'var(--tg-theme-button-color)', color: 'white' };

export default App;



