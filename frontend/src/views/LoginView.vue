<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="auth-bg-overlay" />
    </div>
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-logo">
          <img src="/hk-emblem.png" alt="香港區旗紫荊花" class="brand-emblem" />
          <h1>香港停車場系統</h1>
          <p>HK Parking Management</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="用戶名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="請輸入用戶名"
              prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item label="密碼" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="請輸入密碼"
              prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="auth-btn"
            @click="handleLogin"
          >
            登入
          </el-button>
        </el-form>

        <div class="auth-footer">
          還沒有帳號？
          <router-link to="/register">立即註冊</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '請輸入用戶名', trigger: 'blur' }],
  password: [{ required: true, message: '請輸入密碼', trigger: 'blur' }],
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await authStore.login(form)
      ElMessage.success('登入成功，歡迎回來！')
      router.push('/')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      ElMessage.error(msg || '登入失敗，請檢查用戶名和密碼')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #eef6ff 0%, #f8fcff 52%, #eef5ff 100%);
}

.auth-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 20% 50%, rgba(47, 126, 247, 0.16) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(120, 186, 255, 0.2) 0%, transparent 56%);
}

.auth-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  padding: 16px;
}

.auth-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #d7e5f7;
  border-radius: 16px;
  padding: 40px 36px;
  backdrop-filter: blur(20px);
  box-shadow: 0 24px 48px rgba(47, 126, 247, 0.14);
}

.auth-logo {
  text-align: center;
  margin-bottom: 36px;
}

.brand-emblem {
  width: 46px;
  height: 46px;
  object-fit: contain;
}

.auth-logo h1 {
  font-size: 22px;
  font-weight: 700;
  color: #1f3552;
  margin: 12px 0 4px;
}
.auth-logo p {
  font-size: 13px;
  color: #5e7898;
  letter-spacing: 1px;
}

:deep(.el-form-item__label) {
  color: #5e7898 !important;
  font-size: 13px;
}

.auth-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  margin-top: 8px;
  border-radius: 8px;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 13px;
  color: #5e7898;
}
.auth-footer a {
  color: #4f8ef7;
  text-decoration: none;
  font-weight: 500;
}
.auth-footer a:hover {
  text-decoration: underline;
}
</style>
