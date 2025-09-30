import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('https://functions.poehali.dev/9b37b884-0509-45ec-a9e2-d2e32b25bdb1', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: isLogin ? 'login' : 'register',
          username,
          password,
          full_name: fullName,
          email,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Ошибка при выполнении запроса');
      }

      localStorage.setItem('user_token', data.token);
      localStorage.setItem('user_data', JSON.stringify(data.user));

      toast({
        title: isLogin ? 'Вход выполнен' : 'Регистрация успешна',
        description: `Добро пожаловать, ${data.user.username}!`,
      });

      navigate('/');
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Ошибка',
        description: error instanceof Error ? error.message : 'Произошла ошибка',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center mx-auto mb-4">
            <Icon name="Brain" size={32} className="text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold mb-2">ИИпомогатор</h1>
          <p className="text-muted-foreground">
            {isLogin ? 'Войдите в свой аккаунт' : 'Создайте новый аккаунт'}
          </p>
          {!isLogin && (
            <div className="mt-4 p-3 bg-primary/10 rounded-lg">
              <p className="text-sm font-medium text-primary">
                🎁 При регистрации: 15 бесплатных запросов вместо 10!
              </p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">Логин</Label>
            <Input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Введите логин"
              required
              minLength={3}
            />
          </div>

          {!isLogin && (
            <>
              <div className="space-y-2">
                <Label htmlFor="fullName">Полное имя</Label>
                <Input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Введите ваше имя"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email (необязательно)</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Введите email"
                />
              </div>
            </>
          )}

          <div className="space-y-2">
            <Label htmlFor="password">Пароль</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введите пароль"
              required
              minLength={6}
            />
            {!isLogin && (
              <p className="text-xs text-muted-foreground">
                Минимум 6 символов
              </p>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Icon name="Loader2" size={18} className="mr-2 animate-spin" />
                Загрузка...
              </>
            ) : (
              <>{isLogin ? 'Войти' : 'Зарегистрироваться'}</>
            )}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-sm text-primary hover:underline"
          >
            {isLogin ? 'Нет аккаунта? Зарегистрируйтесь' : 'Уже есть аккаунт? Войдите'}
          </button>
        </div>

        <div className="mt-4 text-center">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="text-sm"
          >
            ← Вернуться на главную
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default Auth;