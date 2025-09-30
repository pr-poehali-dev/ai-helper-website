import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import Icon from '@/components/ui/icon';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const Index = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Привет! Я ИИпомогатор. Задайте мне любой вопрос или опишите задачу, которую нужно решить.',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [requestsUsed, setRequestsUsed] = useState(0);
  const [paidRequests, setPaidRequests] = useState(0);
  const [userId, setUserId] = useState('');
  const [activeSection, setActiveSection] = useState('home');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let storedUserId = localStorage.getItem('ai_helper_user_id');
    if (!storedUserId) {
      storedUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('ai_helper_user_id', storedUserId);
    }
    setUserId(storedUserId);
    
    if (storedUserId) {
      fetch(`https://functions.poehali.dev/f78ea238-e198-40ae-9c1a-788100fd245e?user_id=${storedUserId}`)
        .then(res => res.json())
        .then(data => {
          setRequestsUsed(data.free_requests_used || 0);
          setPaidRequests(data.paid_requests_available || 0);
        })
        .catch(err => console.error('Error loading user stats:', err));
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch('https://functions.poehali.dev/80ffdfe3-67c3-452b-b349-b10146da1cc3', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId,
        },
        body: JSON.stringify({
          message: currentInput,
          user_id: userId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error('Лимит бесплатных запросов исчерпан. Приобретите дополнительные запросы в разделе Тарифы.');
        }
        throw new Error(data.error || 'Ошибка получения ответа');
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.reply,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, aiMessage]);
      
      if (data.usage) {
        setRequestsUsed(data.usage.free_requests_used);
        setPaidRequests(data.usage.paid_requests_available);
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Произошла ошибка: ${error instanceof Error ? error.message : 'Неизвестная ошибка'}. Убедитесь, что добавлен API ключ OpenAI в секреты проекта.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const features = [
    {
      icon: 'MessageSquare',
      title: 'Диалоговый интерфейс',
      description: 'Общайтесь с ИИ как с человеком',
    },
    {
      icon: 'Zap',
      title: 'Быстрые ответы',
      description: 'Мгновенная обработка запросов',
    },
    {
      icon: 'Brain',
      title: 'Умный анализ',
      description: 'Глубокое понимание контекста',
    },
    {
      icon: 'Shield',
      title: 'Безопасность данных',
      description: 'Защита вашей информации',
    },
  ];

  const pricingPlans = [
    {
      name: 'Бесплатно',
      price: '0 ₽',
      requests: '15 запросов',
      requestsCount: 0,
      priceNum: 0,
      packageType: 'free',
      period: 'в сутки',
      features: ['Базовые функции ИИ', 'Обновление каждые 24 часа', 'Стандартная скорость'],
      popular: false,
    },
    {
      name: 'Стандарт',
      price: '399 ₽',
      requests: '40 запросов',
      requestsCount: 40,
      priceNum: 399,
      packageType: 'standard',
      period: 'единоразово',
      features: ['Все функции ИИ', 'Без временных ограничений', 'Приоритетная обработка', 'Поддержка 24/7'],
      popular: true,
    },
    {
      name: 'Про',
      price: '749 ₽',
      requests: '80 запросов',
      requestsCount: 80,
      priceNum: 749,
      packageType: 'pro',
      period: 'единоразово',
      features: ['Расширенные функции', 'Максимальная скорость', 'Приоритет в очереди', 'Персональный менеджер'],
      popular: false,
    },
  ];

  const handlePurchase = async (plan: typeof pricingPlans[0]) => {
    if (plan.priceNum === 0) return;
    
    try {
      const response = await fetch('https://functions.poehali.dev/cc0f5641-ce74-4742-8f24-578467e7b288', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          package_type: plan.packageType,
          amount: plan.priceNum,
          requests_count: plan.requestsCount,
          description: `${plan.name} - ${plan.requests}`
        }),
      });

      const data = await response.json();

      if (response.ok && data.payment_url) {
        window.location.href = data.payment_url;
      } else {
        alert(`Ошибка: ${data.error}`);
      }
    } catch (error) {
      alert(`Ошибка создания платежа: ${error instanceof Error ? error.message : 'Неизвестная ошибка'}`);
    }
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'home':
        return (
          <div className="space-y-8">
            <div className="text-center space-y-4 py-12">
              <div className="inline-flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-full">
                <Icon name="Sparkles" size={18} className="text-primary" />
                <span className="text-sm font-medium">Искусственный интеллект нового поколения</span>
              </div>
              <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
                ИИ<span className="text-primary">помогатор</span>
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Универсальный ИИ-ассистент для решения ваших задач. От простых вопросов до сложного анализа.
              </p>
            </div>

            <Card className="bg-card/50 backdrop-blur border-border/50 shadow-xl">
              <div className="p-4 border-b border-border/50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                    <Icon name="Bot" size={20} className="text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Чат с ИИ</h3>
                    <p className="text-xs text-muted-foreground">Онлайн</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="gap-1">
                    <Icon name="Zap" size={12} />
                    {requestsUsed}/15 запросов
                  </Badge>
                  {paidRequests > 0 && (
                    <Badge variant="default" className="gap-1">
                      <Icon name="Crown" size={12} />
                      +{paidRequests}
                    </Badge>
                  )}
                </div>
              </div>

              <ScrollArea className="h-[400px] p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          message.role === 'user' ? 'bg-secondary' : 'bg-primary/20'
                        }`}
                      >
                        <Icon name={message.role === 'user' ? 'User' : 'Bot'} size={16} />
                      </div>
                      <div
                        className={`rounded-2xl px-4 py-3 max-w-[80%] ${
                          message.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                        }`}
                      >
                        <p className="text-sm leading-relaxed">{message.content}</p>
                        <span className="text-xs opacity-70 mt-1 block">
                          {message.timestamp.toLocaleTimeString('ru-RU', {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                    </div>
                  ))}
                  {isTyping && (
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                        <Icon name="Bot" size={16} />
                      </div>
                      <div className="bg-muted rounded-2xl px-4 py-3">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              <div className="p-4 border-t border-border/50">
                <div className="mb-3">
                  <Progress value={(requestsUsed / 15) * 100} className="h-1" />
                  <p className="text-xs text-muted-foreground mt-1">
                    Осталось {15 - requestsUsed} бесплатных запросов сегодня
                  </p>
                </div>
                <div className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Напишите ваш вопрос..."
                    className="flex-1"
                  />
                  <Button onClick={handleSend} size="icon" className="flex-shrink-0">
                    <Icon name="Send" size={18} />
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        );

      case 'features':
        return (
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <h2 className="text-4xl font-bold">Возможности платформы</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                ИИпомогатор предлагает широкий спектр функций для эффективного решения задач
              </p>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              {features.map((feature, index) => (
                <Card key={index} className="p-6 hover:shadow-lg transition-shadow">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                    <Icon name={feature.icon as any} size={24} className="text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'pricing':
        return (
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <h2 className="text-4xl font-bold">Тарифы</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Выберите подходящий план для ваших задач
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
              {pricingPlans.map((plan, index) => (
                <Card
                  key={index}
                  className={`p-6 relative ${
                    plan.popular ? 'border-primary shadow-xl scale-105' : ''
                  }`}
                >
                  {plan.popular && (
                    <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">
                      Популярный
                    </Badge>
                  )}
                  <div className="text-center space-y-4 mb-6">
                    <h3 className="text-2xl font-bold">{plan.name}</h3>
                    <div>
                      <p className="text-4xl font-bold text-primary">{plan.price}</p>
                      <p className="text-sm text-muted-foreground mt-1">{plan.period}</p>
                    </div>
                    <p className="text-lg font-semibold">{plan.requests}</p>
                  </div>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <Icon name="Check" size={18} className="text-primary mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button 
                    className="w-full" 
                    variant={plan.popular ? 'default' : 'outline'}
                    onClick={() => handlePurchase(plan)}
                    disabled={plan.priceNum === 0}
                  >
                    {plan.priceNum === 0 ? 'Текущий план' : 'Купить'}
                  </Button>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'creator':
        return (
          <div className="space-y-8 max-w-4xl mx-auto">
            <div className="text-center space-y-4">
              <h2 className="text-4xl font-bold">Создатель</h2>
            </div>
            <Card className="p-8">
              <div className="flex flex-col md:flex-row gap-8 items-center">
                <div className="w-32 h-32 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center flex-shrink-0">
                  <Icon name="User" size={48} />
                </div>
                <div className="flex-1 text-center md:text-left">
                  <h3 className="text-2xl font-bold mb-2">Егор Селицкий</h3>
                  <p className="text-muted-foreground mb-4">Основатель и CEO ИИпомогатор</p>
                </div>
              </div>
            </Card>
          </div>
        );

      case 'help':
        return (
          <div className="space-y-8 max-w-4xl mx-auto">
            <div className="text-center space-y-4">
              <h2 className="text-4xl font-bold">Помощь</h2>
              <p className="text-lg text-muted-foreground">
                Ответы на частые вопросы
              </p>
            </div>
            <div className="space-y-4">
              {[
                {
                  q: 'Как работает ИИпомогатор?',
                  a: 'ИИпомогатор использует передовые модели машинного обучения для анализа вашего запроса и предоставления точного ответа.',
                },
                {
                  q: 'Что происходит после 15 бесплатных запросов?',
                  a: 'После использования 15 бесплатных запросов вам нужно приобрести один из платных пакетов для продолжения работы.',
                },
                {
                  q: 'Как оплатить дополнительные запросы?',
                  a: 'Перейдите в раздел "Тарифы", выберите подходящий план и оплатите через удобный способ оплаты.',
                },
                {
                  q: 'Безопасны ли мои данные?',
                  a: 'Да, мы используем современные методы шифрования и не передаем ваши данные третьим лицам.',
                },
              ].map((item, index) => (
                <Card key={index} className="p-6">
                  <h3 className="font-semibold text-lg mb-2 flex items-center gap-2">
                    <Icon name="HelpCircle" size={20} className="text-primary" />
                    {item.q}
                  </h3>
                  <p className="text-muted-foreground pl-7">{item.a}</p>
                </Card>
              ))}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-background/80 border-b border-border/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                <Icon name="Brain" size={24} className="text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">ИИпомогатор</span>
            </div>
            <div className="hidden md:flex items-center gap-6">
              {[
                { id: 'home', label: 'Главная', icon: 'Home' },
                { id: 'features', label: 'Функции', icon: 'Sparkles' },
                { id: 'pricing', label: 'Тарифы', icon: 'CreditCard' },
                { id: 'creator', label: 'Создатель', icon: 'User' },
                { id: 'help', label: 'Помощь', icon: 'HelpCircle' },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    activeSection === item.id
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-muted'
                  }`}
                >
                  <Icon name={item.icon as any} size={16} />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <Button onClick={() => navigate('/auth')} variant="outline">
                <Icon name="User" size={16} className="mr-2" />
                Вход / Регистрация
              </Button>
              <Button onClick={() => navigate('/admin/login')} size="icon" variant="ghost">
                <Icon name="Lock" size={16} />
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-12">
        {renderContent()}
      </main>

      <footer className="border-t border-border/50 mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Icon name="Brain" size={20} className="text-primary" />
              <span className="text-sm text-muted-foreground">
                © 2024 ИИпомогатор. Все права защищены.
              </span>
            </div>
            <div className="flex items-center gap-4">
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Политика конфиденциальности
              </a>
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Условия использования
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;