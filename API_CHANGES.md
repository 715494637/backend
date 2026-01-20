# 接口新增和修改方案

> 生成时间: 2025-01-13
> 状态: ✅ 所有前端 API 调用已实现

---

## 一、接口对比分析结果

### 1.1 总体情况

| 项目 | 数量 |
|------|------|
| 前端 API 调用数 | **38 个** |
| 后端已实现数 | **38 个** |
| 缺失接口 | **0 个** |
| 需要修改 | **0 个** |

### 1.2 详细对比清单

| 序号 | 前端方法名 | 后端路径 | 状态 |
|------|-----------|----------|------|
| 1 | `login()` | `POST /auth/login` | ✅ 已实现 |
| 2 | `sendSms()` | `POST /auth/send-sms` | ✅ 已实现 |
| 3 | `register()` | `POST /auth/register` | ✅ 已实现 |
| 4 | `getUsers()` | `GET /users` | ✅ 已实现 |
| 5 | `approveUser()` | `PUT /users/{id}/approve` | ✅ 已实现 |
| 6 | `deleteUser()` | `DELETE /users/{id}` | ✅ 已实现 |
| 7 | `updateUser()` | `PUT /users/{id}` | ✅ 已实现 |
| 8 | `createUserByAdmin()` | `POST /users` | ✅ 已实现 |
| 9 | `getDocuments()` | `GET /documents` | ✅ 已实现 |
| 10 | `createDocument()` | `POST /documents` | ✅ 已实现 |
| 11 | `updateDocument()` | `PUT /documents/{id}` | ✅ 已实现 |
| 12 | `deleteDocument()` | `DELETE /documents/{id}` | ✅ 已实现 |
| 13 | `getRisks()` | `GET /risks` | ✅ 已实现 |
| 14 | `createRisk()` | `POST /risks` | ✅ 已实现 |
| 15 | `updateRisk()` | `PUT /risks/{id}` | ✅ 已实现 |
| 16 | `deleteRisk()` | `DELETE /risks/{id}` | ✅ 已实现 |
| 17 | `getEvidence()` | `GET /evidence` | ✅ 已实现 |
| 18 | `createEvidence()` | `POST /evidence` | ✅ 已实现 |
| 19 | `updateEvidence()` | `PUT /evidence/{id}` | ✅ 已实现 |
| 20 | `deleteEvidence()` | `DELETE /evidence/{id}` | ✅ 已实现 |
| 21 | `getCivilCode()` | `GET /civil-code` | ✅ 已实现 |
| 22 | `createCivilCode()` | `POST /civil-code` | ✅ 已实现 |
| 23 | `updateCivilCode()` | `PUT /civil-code/{id}` | ✅ 已实现 |
| 24 | `deleteCivilCode()` | `DELETE /civil-code/{id}` | ✅ 已实现 |
| 25 | `getEnterprises()` | `GET /enterprises` | ✅ 已实现 |
| 26 | `createEnterprise()` | `POST /enterprises` | ✅ 已实现 |
| 27 | `deleteEnterprise()` | `DELETE /enterprises/{name}` | ✅ 已实现 |
| 28 | `getConfig()` | `GET /config` | ✅ 已实现 |
| 29 | `updateConfig()` | `PUT /config` | ✅ 已实现 |
| 30 | `getPosters()` | `GET /posters` | ✅ 已实现 |
| 31 | `createPoster()` | `POST /posters` | ✅ 已实现 |
| 32 | `deletePoster()` | `DELETE /posters/{id}` | ✅ 已实现 |
| 33 | `getContactQR()` | `GET /contact-qr` | ✅ 已实现 |
| 34 | `createContactQR()` | `POST /contact-qr` | ✅ 已实现 |
| 35 | `deleteContactQR()` | `DELETE /contact-qr/{id}` | ✅ 已实现 |
| 36 | `getSplashImage()` | `GET /splash-image` | ✅ 已实现 |
| 37 | `uploadSplashImage()` | `POST /splash-image` | ✅ 已实现 |
| 38 | `deleteSplashImage()` | `DELETE /splash-image` | ✅ 已实现 |

---

## 二、建议优化项（非必须）

虽然所有接口已实现，以下是建议的优化点：

### 2.1 新增建议接口

| 接口 | 路径 | 用途 | 优先级 |
|------|------|------|--------|
| 获取单个用户 | `GET /users/{id}` | 详情页展示 | 🟡 中 |
| 用户修改密码 | `PUT /users/{id}/password` | 用户安全 | 🟡 中 |
| 获取单个文档 | `GET /documents/{id}` | 详情页 | 🟢 低 |
| 搜索文档 | `GET /documents?q=` | 搜索功能 | 🟢 低 |

### 2.2 建议修改项

| 项目 | 当前状态 | 建议修改 | 原因 |
|------|----------|----------|------|
| 短信发送 | 模拟返回 | 接入真实短信服务 | 功能完善 |
| 密码更新 | 无接口 | 新增 `PUT /users/{id}/password` | 安全需要 |
| 批量操作 | 不支持 | 考虑增加批量删除 | 效率提升 |

---

## 三、接口修改代码示例

### 3.1 新增：获取单个用户接口

**文件**: `backend/app/api/routes.py`

```python
@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
```

### 3.2 新增：修改密码接口

**文件**: `backend/app/api/routes.py`

```python
@router.put("/users/{user_id}/password")
async def change_password(
    user_id: str,
    password_data: dict,  # {"old_password": "...", "new_password": "..."}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户修改密码"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="只能修改自己的密码")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.password != password_data.get("old_password"):
        raise HTTPException(status_code=400, detail="原密码错误")

    user.password = password_data.get("new_password")
    db.commit()

    return {"message": "密码修改成功"}
```

### 3.3 前端添加对应方法

**文件**: `Vite/src/services/apiService.ts`

```typescript
// 获取单个用户
async getUser(userId: string, token: string) {
  return fetchWithErrorHandler(`${API_BASE}/users/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
},

// 修改密码
async changePassword(userId: string, passwordData: { old_password: string; new_password: string }, token: string) {
  return fetchWithErrorHandler(`${API_BASE}/users/${userId}/password`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(passwordData)
  });
}
```

---

## 四、数据库变更（如需）

如需新增密码修改日志功能，可添加表：

```sql
-- 密码修改日志表（可选）
CREATE TABLE password_change_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 五、总结

### ✅ 当前状态

- **38 个前端 API 调用已全部实现**
- **0 个缺失接口**
- **0 个需要紧急修改的接口**

### 📋 如需新增功能

按优先级依次实现：
1. 🟡 获取单个用户接口
2. 🟡 用户修改密码接口
3. 🟢 文档搜索接口
4. 🟢 批量操作接口

---

*文档生成时间: 2025-01-13*
