/**
 * 🏥 7일차: 폐렴 백오피스 프론트엔드 - 백엔드 실시간 API 연결 클라이언트 (최종 조율본)
 * - [보안 규격] JWT Access Token 만료 시 대기열 자동 토큰 리프레시 엔진 활성화
 * - [디자인 가이드] 템플릿 UI의 전용 알림 컴포넌트(utils.showAlert) 및 전역 상태(state) 완벽 연동
 * - [API 매핑] 4일차(Users), 5일차(Patients/Records), 6일차(AI Analysis) 백엔드 라우터 실제 경로 매핑 완료
 */

const API_BASE = '/api/v1';

const apis = {
    isRefreshing: false,
    refreshSubscribers: [],

    subscribeTokenRefresh(cb) {
        this.refreshSubscribers.push(cb);
    },

    onTokenRefreshed(token) {
        this.refreshSubscribers.map(cb => cb(token));
        this.refreshSubscribers = [];
    },

    async request(url, options = {}, skipAlert = false) {
        const headers = { ...options.headers };
        if (state.token) {
            headers['Authorization'] = `Bearer ${state.token}`;
        }

        try {
            const response = await fetch(`${API_BASE}${url}`, { ...options, headers });
            
            // 401 Unauthorized 감지 시 실시간 토큰 자동 갱신 및 대기열 재실행 가동
            if (response.status === 401) {
                if (url === '/auth/login') {
                    return { status: 401 };
                }
                
                if (!state.token) {
                    await logout();
                    return null;
                }

                if (this.isRefreshing) {
                    return new Promise((resolve) => {
                        this.subscribeTokenRefresh(token => {
                            headers['Authorization'] = `Bearer ${token}`;
                            resolve(this.request(url, options, skipAlert));
                        });
                    });
                }

                this.isRefreshing = true;
                try {
                    const refreshResponse = await fetch(`${API_BASE}/auth/token/refresh`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    if (refreshResponse.ok) {
                        const data = await refreshResponse.json();
                        state.token = data.access_token;
                        localStorage.setItem('token', state.token);
                        
                        this.isRefreshing = false;
                        this.onTokenRefreshed(state.token);
                        
                        headers['Authorization'] = `Bearer ${state.token}`;
                        return await this.request(url, options, skipAlert);
                    } else {
                        this.isRefreshing = false;
                        await logout();
                        return null;
                    }
                } catch (refreshErr) {
                    this.isRefreshing = false;
                    await logout();
                    return null;
                }
            }
            
            if (!response.ok) {
                let error;
                try {
                    error = await response.json();
                } catch (e) {
                    error = { detail: '서버 응답 처리 중 오류가 발생했습니다.' };
                }
                
                let msg = error.detail || '요청 중 오류가 발생했습니다.';
                if (Array.isArray(msg)) {
                    msg = msg.map(e => {
                        let text = e.msg;
                        text = text.replace(/^Value error, /, '');
                        text = text.replace(/^Field required, /, '');
                        if (text === 'Field required') text = '필수 입력 항목입니다.';
                        return text;
                    }).join(', ');
                }

                const passwordErrorMessage = "비밀번호는 대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다.";
                if (msg.includes(passwordErrorMessage)) {
                    msg = passwordErrorMessage;
                } else if (response.status >= 500) {
                    msg = "잠시후 다시 시도해주세요.";
                }

                const errObj = new Error(msg);
                errObj.status = response.status;
                throw errObj;
            }
            if (response.status === 204) return null;
            return await response.json();
        } catch (err) {
            if (url !== '/auth/login' && !skipAlert) {
                utils.showAlert(err.message, 'error', '오류');
            }
            throw err;
        }
    },

    // ==========================================
    // 👤 1. 회원 인증 및 계정 관리 API (4일차 명세)
    // ==========================================
    async signup(userData) {
        return await this.request('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        }, true);
    },

    async login(email, password) {
        return await this.request('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        }, true);
    },

    async refresh() {
        return await fetch(`${API_BASE}/auth/token/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
    },

    async logout() {
        return await this.request('/auth/logout', { method: 'POST' });
    },

    async getMe() {
        return await this.request('/users/me');
    },

    async updateMe(userData) {
        return await this.request('/users/me', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        }, true);
    },

    async updatePassword(passwordData) {
        return await this.request('/users/me/password', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(passwordData)
        }, true);
    },

    async deleteMe() {
        return await this.request('/users/me', { method: 'DELETE' });
    },

    // ==========================================
    // 🏥 2. 환자 인적정보 관리 API (5일차 명세)
    // ==========================================
    async createPatient(patientData) {
        return await this.request('/patients', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(patientData)
        });
    },

    async getPatients(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await this.request(`/patients${query ? `?${query}` : ''}`);
    },

    async getPatient(patientId) {
        return await this.request(`/patients/${patientId}`);
    },

    async updatePatient(patientId, patientData) {
        return await this.request(`/patients/${patientId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(patientData)
        });
    },

    async deletePatient(patientId) {
        return await this.request(`/patients/${patientId}`, { method: 'DELETE' });
    },

    // ==========================================
    // 📁 3. 진료 기록 접수 및 업로드 API (5일차 명세)
    // ==========================================
    async createMedicalRecord(formData) {
        return await this.request('/medical-records', {
            method: 'POST',
            body: formData
        });
    },

    async getPatientMedicalRecords(patientId) {
        return await this.request(`/patients/${patientId}/medical-records`);
    },

    async getMedicalRecord(recordId) {
        return await this.request(`/medical-records/${recordId}`);
    },

    // ==========================================
    // 🔬 4. PyTorch 실시간 AI 폐렴 추론 API (6일차 명세 매핑 보정 완료)
    // ==========================================
    async predictPneumonia(recordId) {
        // 🚨 [경로 보정] /medical-records/.../predict ➡️ /ai-analysis/{recordId}
        return await this.request(`/ai-analysis/${recordId}`, { method: 'POST' });
    },

    async getMedicalRecordAnalyses(recordId) {
        try {
            // 🚨 [안전성 극대화] 
            // 1. skipAlert를 true로 쏘아, AI 진단 결과가 아직 없을 때(404 에러 시) 불필요한 오류 경고창 알림이 뜨는 현상 차단.
            // 2. 단일 객체(Object {}) 응답이 오더라도 배열(Array []) 형태로 자동 래핑하여 .map() 에러 원천 해결.
            const result = await this.request(`/ai-analysis/records/${recordId}`, {}, true);
            if (!result) return [];
            return Array.isArray(result) ? result : [result];
        } catch (err) {
            console.warn("AI Analyses Fetch Info (Normal if not analyzed yet):", err);
            return [];
        }
    },

    // ==========================================
    // 👑 5. 어드민 전용 회원 통제 API (4일차 명세)
    // ==========================================
    async adminGetUsers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await this.request(`/users${query ? `?${query}` : ''}`);
    },

    async adminUpdateUserRole(userId, roleData) {
        return await this.request(`/users/${userId}/role`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(roleData)
        });
    }
};

// 템플릿 환경에 안전하게 매핑되도록 전역 객체 바인딩 선언
window.apis = apis;