<template>
  <div class="auth-page">
    <div class="auth-bg" />
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-logo">
          <el-icon :size="40" color="#4f8ef7"><Location /></el-icon>
          <h1>創建帳號</h1>
          <p>Join HK Parking Management</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent="handleRegister"
        >
          <el-form-item label="用戶名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="請輸入用戶名（3-20字符）"
              prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item label="電子郵件" prop="email">
            <el-input
              v-model="form.email"
              type="email"
              placeholder="請輸入電子郵件"
              prefix-icon="Message"
              size="large"
            />
          </el-form-item>
          <el-form-item label="手機號碼（可選）" prop="phone">
            <el-input
              v-model="form.phone"
              placeholder="請輸入手機號碼"
              prefix-icon="Phone"
              size="large"
            />
          </el-form-item>
          <el-form-item label="密碼" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="請設置密碼（至少8位）"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          <el-form-item label="確認密碼" prop="password2">
            <el-input
              v-model="form.password2"
              type="password"
              placeholder="請再次輸入密碼"
              prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleRegister"
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="auth-btn"
            @click="handleRegister"
          >
            立即註冊
          </el-button>
        </el-form>

        <div class="auth-footer">
          已有帳號？
          <router-link to="/login">立即登入</router-link>
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

const form = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  password2: '',
})

const validatePass2 = (_: unknown, value: string, callback: (e?: Error) => void) => {
  if (value !== form.password) {
    callback(new Error('兩次密碼不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '請輸入用戶名', trigger: 'blur' },
    { min: 3, max: 20, message: '用戶名長度為3-20字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '請輸入電子郵件', trigger: 'blur' },
    { type: 'email', message: '請輸入有效的電子郵件', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '請輸入密碼', trigger: 'blur' },
    { min: 8, message: '密碼至少8位', trigger: 'blur' },
  ],
  password2: [
    { required: true, message: '請確認密碼', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' },
  ],
}

async function handleRegister() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await authStore.register(form)
      ElMessage.success('註冊成功，歡迎加入！')
      router.push('/')
    } catch (err: unknown) {
      const errData = (err as { response?: { data?: Record<string, unknown> } })?.response?.data
      let msg = '註冊失敗，請稍後再試'
      if (errData) {
        const firstKey = Object.keys(errData)[0]
        const firstVal = errData[firstKey]
        if (Array.isArray(firstVal)) msg = String(firstVal[0])
        else if (typeof firstVal === 'string') msg = firstVal
      }
      ElMessage.error(msg)
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
  background: linear-gradient(135deg, #eef6ff 0%, #f8fcff 52%, #eef5ff 100%);
  position: relative;
}
.auth-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 80% 50%, rgba(47, 126, 247, 0.16) 0%, transparent 50%),
    radial-gradient(ellipse at 20% 80%, rgba(120, 186, 255, 0.2) 0%, transparent 56%);
}
.auth-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 440px;
  padding: 16px;
}
.auth-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #d7e5f7;
  border-radius: 16px;
  padding: 36px;
  backdrop-filter: blur(20px);
  box-shadow: 0 24px 48px rgba(47, 126, 247, 0.14);
}
.auth-logo {
  text-align: center;
  margin-bottom: 28px;
}
.auth-logo h1 {
  font-size: 22px;
  font-weight: 700;
  color: #1f3552;
  margin: 10px 0 4px;
}
.auth-logo p { font-size: 13px; color: #5e7898; letter-spacing: 1px; }
:deep(.el-form-item__label) { color: #5e7898 !important; font-size: 13px; }
.auth-btn { width: 100%; height: 46px; font-size: 16px; margin-top: 8px; border-radius: 8px; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 13px; color: #5e7898; }
.auth-footer a { color: #4f8ef7; text-decoration: none; font-weight: 500; }
</style>
