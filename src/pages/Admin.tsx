import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import Icon from '@/components/ui/icon';

const Admin = () => {
  const [admin, setAdmin] = useState<any>(null);
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
    } catch {
      navigate('/admin/login');
    }
  }, [navigate]);

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
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Icon name="Users" size={24} className="text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">—</p>
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
                <p className="text-2xl font-bold">—</p>
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
                <p className="text-2xl font-bold">—</p>
                <p className="text-sm text-muted-foreground">Доход</p>
              </div>
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <h2 className="text-xl font-bold mb-4">Добро пожаловать, {admin.full_name}!</h2>
          <p className="text-muted-foreground">
            Панель администратора ИИпомогатора. Здесь вы можете управлять платформой и отслеживать статистику.
          </p>
          <div className="mt-6 p-4 bg-muted/50 rounded-lg">
            <p className="text-sm">
              <strong>Важно:</strong> Для работы платежной системы добавьте секреты:
            </p>
            <ul className="text-sm mt-2 space-y-1 ml-4">
              <li>• YOOKASSA_SHOP_ID — ID магазина в ЮKassa</li>
              <li>• YOOKASSA_SECRET_KEY — Секретный ключ ЮKassa</li>
              <li>• OPENAI_API_KEY — API ключ OpenAI</li>
            </ul>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default Admin;