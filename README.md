# Restaurant Backend (Django + DRF + JWT)

A REST API backend for the Flutter restaurant app: email/password auth (JWT)
and a menu system that staff/admin manage from the Django admin panel.

## Project structure

```
restaurant_backend/
├── manage.py
├── requirements.txt
├── restaurant_backend/        # project settings, root urls
├── accounts/                  # custom User model + register/login/profile
│   ├── models.py              # User (email as login, phone_number field)
│   ├── managers.py            # UserManager (create_user/create_superuser)
│   ├── serializers.py         # RegisterSerializer, LoginSerializer, UserSerializer
│   ├── views.py                # RegisterView, LoginView, ProfileView
│   └── urls.py
└── menu/                      # menu items admins add, users browse
    ├── models.py               # MenuItem (name, description, image, size, price)
    ├── permissions.py          # IsAdminOrReadOnly
    ├── serializers.py          # MenuItemSerializer
    ├── views.py                 # MenuItemViewSet (list/create/update/delete)
    └── urls.py
```

## 1. Setup

```bash
cd restaurant_backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit SECRET_KEY etc.

python manage.py makemigrations accounts menu
python manage.py migrate

python manage.py createsuperuser   # prompts for email + password (this is your admin login)

python manage.py runserver
```

The API is now live at `http://127.0.0.1:8000/api/`.
The admin panel — where you add/edit/hide menu items — is at
`http://127.0.0.1:8000/admin/`, log in with the superuser you just created.

If you're testing from a physical phone or emulator, run
`python manage.py runserver 0.0.0.0:8000` and point Flutter at your machine's
LAN IP (Android emulator: use `10.0.2.2` instead of `localhost`).

## 2. API Reference

All request/response bodies are JSON. Protected endpoints require:
`Authorization: Bearer <access_token>`

### Auth

| Method | Endpoint | Auth? | Body | Notes |
|---|---|---|---|---|
| POST | `/api/auth/register/` | No | `email, password, first_name, last_name, phone_number` | Returns `user` + `tokens` |
| POST | `/api/auth/login/` | No | `email, password` | Returns `user` + `tokens` |
| POST | `/api/auth/token/refresh/` | No | `refresh` | Returns a new `access` token |
| GET | `/api/auth/profile/` | Yes | – | Returns the logged-in user |
| PATCH | `/api/auth/profile/` | Yes | any of `first_name, last_name, phone_number` | Update profile |

**Register example**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","password":"secret123","first_name":"Jane","last_name":"Doe","phone_number":"+1234567890"}'
```
```json
{
  "user": {"id": 1, "email": "jane@example.com", "first_name": "Jane", "last_name": "Doe", "phone_number": "+1234567890"},
  "tokens": {"access": "eyJ...", "refresh": "eyJ..."}
}
```

**Login example**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","password":"secret123"}'
```

### Menu

| Method | Endpoint | Auth? | Notes |
|---|---|---|---|
| GET | `/api/menu/` | Yes (any logged-in user) | List items. `?search=pizza` filters by name/description |
| GET | `/api/menu/<id>/` | Yes | Single item |
| POST | `/api/menu/` | Yes, staff/admin only | Create item (multipart form for image upload) |
| PATCH | `/api/menu/<id>/` | Yes, staff/admin only | Update item |
| DELETE | `/api/menu/<id>/` | Yes, staff/admin only | Delete item |

Response shape matches the Flutter `MenuItemModel` exactly:
```json
{
  "id": 1,
  "name": "Margherita Pizza",
  "description": "Classic pizza topped with fresh tomatoes, mozzarella, and basil.",
  "imageUrl": "http://127.0.0.1:8000/media/menu_images/pizza.jpg",
  "size": "Medium (12 inch)",
  "price": "12.99",
  "is_available": true
}
```

Non-staff users only ever see items where `is_available = true` — an admin
can hide an item instantly from the admin panel without deleting it.

## 3. Adding menus as the admin

You don't need any extra endpoints for this — just:
1. Go to `http://127.0.0.1:8000/admin/`
2. Click **Menu items → Add menu item**
3. Fill in name, description, upload an image, size, price → Save

It shows up in the app's `/api/menu/` response immediately.

## 4. Wiring this into the Flutter app

Replace `FakeAuthRepository` / `FakeMenuRepository` with real HTTP calls.
Add `http: ^1.2.0` to `pubspec.yaml`, then something like:

```dart
class ApiAuthRepository implements AuthRepository {
  final String baseUrl = 'http://10.0.2.2:8000/api/auth'; // Android emulator

  @override
  Future<UserModel> login(LoginRequestModel request) async {
    final res = await http.post(
      Uri.parse('$baseUrl/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': request.email, 'password': request.password}),
    );
    if (res.statusCode != 200) {
      throw Exception(jsonDecode(res.body).values.first.toString());
    }
    final data = jsonDecode(res.body);
    // TODO: persist data['tokens']['access'] / ['refresh'] (e.g. flutter_secure_storage)
    // and attach 'Authorization: Bearer <access>' to subsequent requests.
    final u = data['user'];
    return UserModel(
      email: u['email'],
      firstName: u['first_name'],
      lastName: u['last_name'],
      phoneNumber: u['phone_number'],
    );
  }
  // signup() follows the same pattern against /register/
}
```

Then swap it in `providers/providers.dart`:
```dart
final authRepositoryProvider = Provider<AuthRepository>((ref) => ApiAuthRepository());
final menuRepositoryProvider = Provider<MenuRepository>((ref) => ApiMenuRepository());
```

Nothing else in the app changes — the ViewModels and Views only depend on
the abstract `AuthRepository`/`MenuRepository` interfaces.

Want me to write the full `ApiAuthRepository` + `ApiMenuRepository` (with
token storage and auto-attached auth headers) for you? Happy to add that next.

## 5. Production notes

- Set `DEBUG=False` and a real `SECRET_KEY` in `.env`.
- Set `ALLOWED_HOSTS` to your real domain.
- Swap SQLite for Postgres (`DATABASES` in `settings.py`).
- Restrict `CORS_ALLOW_ALL_ORIGINS` to your actual origins.
- Serve `MEDIA_ROOT` from real storage (S3, etc.) instead of local disk.
