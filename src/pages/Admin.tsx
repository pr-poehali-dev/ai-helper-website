import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface Stats {
  users: {
    total: number;
    new_by_day: Array<{ date: string; count: number }>;
  };
  messages: {
    total: number;
  };
  revenue: {
    total: number;
    pending: number;
    by_package: Array<{ package: string; count: number; revenue: number }>;
  };
  purchases: {
    total: number;
  };
  requests: {
    free_used: number;
    paid_remaining: number;
  };
}

const Admin = () => {
  const [admin, setAdmin] = useState<any>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    const adminData = localStorage.getItem('admin_user');

    if (!token || !adminData) {
      navigate('/admin/login');
      return;
    }

    try {
      setAdmin(JSON.parse(adminData));
      loadStats(token);
    } catch {
      navigate('/admin/login');
    }
  }, [navigate]);

  const loadStats = async (token: string) => {
    try {
      const response = await fetch('https://functions.poehali.dev/379c4493-5514-42da-8977-17bc957d3c34', {
        method: 'GET',
        headers: {
          'X-Admin-Token': token,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    navigate('/');
  };

  if (!admin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border/50 bg-card/50 backdrop-blur">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <Icon name="Brain" size={24} className="text-primary-foreground" />
            </div>
            <div>
              <h1 className="font-bold">Панель администратора</h1>
              <p className="text-xs text-muted-foreground">ИИпомогатор</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium">{admin.full_name}</p>
              <p className="text-xs text-muted-foreground">@{admin.username}</p>
            </div>
            <Button variant="outline" onClick={handleLogout}>
              <Icon name="LogOut" size={16} className="mr-2" />
              Выйти
            </Button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Icon name="Loader2" size={32} className="animate-spin text-primary" />
          </div>
        ) : (
          <>
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <Card className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                    <Icon name="Users" size={24} className="text-primary" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats?.users.total || 0}</p>
                    <p className="text-sm text-muted-foreground">Пользователей</p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                    <Icon name="MessageSquare" size={24} className="text-secondary" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats?.messages.total || 0}</p>
                    <p className="text-sm text-muted-foreground">Сообщений</p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center">
                    <Icon name="DollarSign" size={24} className="text-green-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats?.revenue.total.toFixed(0) || 0} ₽</p>
                    <p className="text-sm text-muted-foreground">Доход</p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center">
                    <Icon name="ShoppingCart" size={24} className="text-orange-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats?.purchases.total || 0}</p>
                    <p className="text-sm text-muted-foreground">Покупок</p>
                  </div>
                </div>
              </Card>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Продажи по тарифам</h3>
                <div className="space-y-3">
                  {stats?.revenue.by_package.map((pkg, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div>
                        <p className="font-medium capitalize">{pkg.package}</p>
                        <p className="text-xs text-muted-foreground">{pkg.count} покупок</p>
                      </div>
                      <Badge variant="secondary" className="text-base">
                        {pkg.revenue.toFixed(0)} ₽
                      </Badge>
                    </div>
                  ))}
                  {(!stats?.revenue.by_package || stats.revenue.by_package.length === 0) && (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      Пока нет продаж
                    </p>
                  )}
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Использование запросов</h3>
                <div className="space-y-4">
                  <div className="p-4 bg-primary/10 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Icon name="Zap" size={20} className="text-primary" />
                        <span className="font-medium">Бесплатных использовано</span>
                      </div>
                      <span className="text-2xl font-bold">{stats?.requests.free_used || 0}</span>
                    </div>
                  </div>

                  <div className="p-4 bg-secondary/10 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Icon name="Crown" size={20} className="text-secondary" />
                        <span className="font-medium">Платных осталось</span>
                      </div>
                      <span className="text-2xl font-bold">{stats?.requests.paid_remaining || 0}</span>
                    </div>
                  </div>
                </div>
              </Card>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Новые пользователи (30 дней)</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {stats?.users.new_by_day.map((day, index) => (
                    <div key={index} className="flex items-center justify-between p-2 hover:bg-muted/50 rounded">
                      <span className="text-sm">{new Date(day.date).toLocaleDateString('ru-RU')}</span>
                      <Badge variant="outline">{day.count}</Badge>
                    </div>
                  ))}
                  {(!stats?.users.new_by_day || stats.users.new_by_day.length === 0) && (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      Нет данных
                    </p>
                  )}
                </div>
              </Card>

              <Card className="p-6">
                <h2 className="text-lg font-bold mb-4">Информация</h2>
                <p className="text-muted-foreground mb-4">
                  Добро пожаловать в панель администратора ИИпомогатора!
                </p>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm font-medium mb-2">Важно для запуска:</p>
                  <ul className="text-sm space-y-1 ml-4">
                    <li>• YOOKASSA_SHOP_ID</li>
                    <li>• YOOKASSA_SECRET_KEY</li>
                    <li>• OPENAI_API_KEY</li>
                  </ul>
                  <p className="text-xs text-muted-foreground mt-3">
                    Webhook URL для ЮKassa:<br />
                    <code className="text-xs">https://functions.poehali.dev/47281ed3-b30a-490f-90c5-3f70c852f967</code>
                  </p>
                </div>
              </Card>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default Admin;