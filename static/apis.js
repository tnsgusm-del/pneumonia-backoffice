/**
 * API 호출을 담당하는 모듈입니다.
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

    async predictPneumonia(recordId) {
        return await this.request(`/medical-records/${recordId}/predict`, { method: 'POST' });
    },

    async getMedicalRecordAnalyses(recordId) {
        return await this.request(`/medical-records/${recordId}/analyses`);
    },

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