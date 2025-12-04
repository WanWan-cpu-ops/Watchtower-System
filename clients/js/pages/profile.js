// 个人资料页面逻辑 - 含实名认证功能
class ProfilePage {
    constructor() {
        this.init();
        this.verificationStatus = null;
        this.smsCountdown = 0;
        this.smsTimer = null;
        this.formDataChanged = false;
    }
    
    init() {
        this.setupEventListeners();
        this.loadVerificationStatus();
        this.updateProfileInfo();
    }
    
    setupEventListeners() {
        // 完善信息按钮点击事件
        document.getElementById('perfect-info-btn').addEventListener('click', () => {
            this.openVerificationModal();
        });
        
        // 实名认证表单提交事件
        document.getElementById('verification-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitVerificationForm();
        });
        
        // 发送验证码按钮点击事件
        document.getElementById('send-code-btn').addEventListener('click', () => {
            this.sendVerificationCode();
        });
        
        // 表单输入框失焦验证
        const formFields = ['real-name', 'id-card', 'phone-number', 'verification-code'];
        formFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            field.addEventListener('blur', (e) => {
                this.validateField(e.target);
                this.formDataChanged = true;
            });
        });
        
        // ESC键关闭弹窗
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.getElementById('verification-modal');
                if (modal.classList.contains('show')) {
                    this.handleModalClose();
                }
            }
        });
        
        // 弹窗关闭事件
        const modal = document.getElementById('verification-modal');
        modal.addEventListener('hide.bs.modal', () => {
            if (this.formDataChanged) {
                this.handleModalClose();
            }
        });
        
        // 协议链接点击事件
        document.getElementById('agreement-link').addEventListener('click', (e) => {
            e.preventDefault();
            this.showAgreement();
        });
    }
    
    // 加载实名认证状态
    loadVerificationStatus() {
        // 优先从本地存储加载
        const savedStatus = app.getLocalStorage('verificationStatus');
        if (savedStatus) {
            this.verificationStatus = savedStatus;
            this.updateVerificationStatusDisplay();
        }
        
        // 从服务器获取最新状态
        this.refreshVerificationStatus();
    }
    
    // 刷新实名认证状态
    refreshVerificationStatus() {
        const user = app.getCurrentUser();
        // 检查WebSocket连接状态
        if (user && ws && ws.readyState === WebSocket.OPEN) {
            const refreshPacket = {
                type: 'refresh_profile',
                data: {
                    username: user.username
                }
            };
            
            ws.send(refreshPacket);
        } else {
            console.log('WebSocket连接未建立，无法刷新个人资料');
        }
    }
    
    // 更新个人资料信息
    updateProfileInfo() {
        const user = app.getCurrentUser();
        if (user) {
            document.getElementById('profile-username').textContent = user.username;
            document.getElementById('profile-permission').textContent = this.getPermissionText(user.permission_level);
        }
    }
    
    // 更新实名认证状态显示
    updateVerificationStatusDisplay() {
        const statusElement = document.getElementById('verification-status');
        const realNameElement = document.getElementById('profile-real-name');
        const idCardElement = document.getElementById('profile-id-card');
        const phoneElement = document.getElementById('profile-phone-number');
        const perfectBtn = document.getElementById('perfect-info-btn');
        
        if (!this.verificationStatus) {
            statusElement.textContent = '未认证';
            statusElement.className = 'status unverified';
            realNameElement.textContent = '未填写';
            idCardElement.textContent = '未填写';
            phoneElement.textContent = '未填写';
            perfectBtn.style.display = 'block';
            return;
        }
        
        // 更新状态显示
        switch (this.verificationStatus.status) {
            case 0:
                statusElement.textContent = '未认证';
                statusElement.className = 'status unverified';
                perfectBtn.style.display = 'block';
                break;
            case 1:
                statusElement.textContent = '审核中';
                statusElement.className = 'status pending';
                perfectBtn.style.display = 'none';
                break;
            case 2:
                statusElement.textContent = '已认证';
                statusElement.className = 'status verified';
                perfectBtn.style.display = 'none';
                break;
            case 3:
                statusElement.textContent = '认证驳回';
                statusElement.className = 'status rejected';
                perfectBtn.style.display = 'block';
                // 显示驳回原因
                if (this.verificationStatus.reason) {
                    app.showToast(`认证驳回原因: ${this.verificationStatus.reason}`, 'error');
                }
                break;
        }
        
        // 更新个人信息显示
        realNameElement.textContent = this.verificationStatus.realName || '未填写';
        idCardElement.textContent = this.verificationStatus.idCard ? this.maskIdCard(this.verificationStatus.idCard) : '未填写';
        phoneElement.textContent = this.verificationStatus.phoneNumber ? this.maskPhoneNumber(this.verificationStatus.phoneNumber) : '未填写';
    }
    
    // 身份证号脱敏
    maskIdCard(idCard) {
        if (!idCard || idCard.length !== 18) return idCard;
        return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2');
    }
    
    // 手机号脱敏
    maskPhoneNumber(phoneNumber) {
        if (!phoneNumber || phoneNumber.length !== 11) return phoneNumber;
        return phoneNumber.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
    }
    
    // 打开实名认证弹窗
    openVerificationModal() {
        // 重置表单
        this.resetVerificationForm();
        
        // 显示弹窗
        const modal = new bootstrap.Modal(document.getElementById('verification-modal'));
        modal.show();
        
        // 自动聚焦到第一个输入框
        setTimeout(() => {
            document.getElementById('real-name').focus();
        }, 100);
        
        this.formDataChanged = false;
    }
    
    // 重置实名认证表单
    resetVerificationForm() {
        const form = document.getElementById('verification-form');
        form.reset();
        
        // 清除错误提示
        const formGroups = form.querySelectorAll('.form-group');
        formGroups.forEach(group => {
            const input = group.querySelector('.form-control');
            const feedback = group.querySelector('.invalid-feedback');
            if (input) input.classList.remove('is-invalid');
            if (feedback) feedback.textContent = '';
        });
        
        // 清除协议复选框错误
        const agreementCheckbox = document.getElementById('agreement-checkbox');
        const agreementFeedback = agreementCheckbox.parentElement.querySelector('.invalid-feedback');
        if (agreementFeedback) agreementFeedback.textContent = '';
    }
    
    // 表单验证
    validateForm() {
        let isValid = true;
        
        // 验证所有字段
        const formFields = ['real-name', 'id-card', 'phone-number', 'verification-code'];
        formFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        // 验证协议勾选
        const agreementCheckbox = document.getElementById('agreement-checkbox');
        if (!agreementCheckbox.checked) {
            const feedback = agreementCheckbox.parentElement.querySelector('.invalid-feedback');
            feedback.textContent = '请阅读并同意《实名认证服务协议》';
            isValid = false;
        } else {
            const feedback = agreementCheckbox.parentElement.querySelector('.invalid-feedback');
            feedback.textContent = '';
        }
        
        return isValid;
    }
    
    // 单个字段验证
    validateField(field) {
        const fieldId = field.id;
        const value = field.value.trim();
        const feedback = field.nextElementSibling;
        let isValid = true;
        
        field.classList.remove('is-invalid');
        feedback.textContent = '';
        
        switch (fieldId) {
            case 'real-name':
                if (!value) {
                    feedback.textContent = '请输入真实姓名';
                    isValid = false;
                } else if (!/^[\u4e00-\u9fa5]{2,10}$/.test(value)) {
                    feedback.textContent = '真实姓名只能包含中文，长度为2-10位';
                    isValid = false;
                }
                break;
                
            case 'id-card':
                if (!value) {
                    feedback.textContent = '请输入身份证号';
                    isValid = false;
                } else if (!this.validateIdCard(value)) {
                    feedback.textContent = '请输入18位有效身份证号（含X/x）';
                    isValid = false;
                }
                break;
                
            case 'phone-number':
                if (!value) {
                    feedback.textContent = '请输入手机号';
                    isValid = false;
                } else if (!/^1[3-9]\d{9}$/.test(value)) {
                    feedback.textContent = '请输入以13/14/15/17/18/19开头的11位手机号';
                    isValid = false;
                }
                break;
                
            case 'verification-code':
                if (!value) {
                    feedback.textContent = '请输入验证码';
                    isValid = false;
                } else if (!/^\d{6}$/.test(value)) {
                    feedback.textContent = '验证码为6位数字';
                    isValid = false;
                }
                break;
        }
        
        if (!isValid) {
            field.classList.add('is-invalid');
        }
        
        return isValid;
    }
    
    // 身份证号高级验证
    validateIdCard(idCard) {
        // 基本格式验证
        if (!/^\d{17}[\dXx]$/.test(idCard)) {
            return false;
        }
        
        // 校验码验证
        const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2];
        const checkCodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2'];
        
        let sum = 0;
        for (let i = 0; i < 17; i++) {
            sum += parseInt(idCard[i]) * weights[i];
        }
        
        const checkCode = checkCodes[sum % 11];
        return checkCode === idCard[17].toUpperCase();
    }
    
    // 发送验证码
    sendVerificationCode() {
        const phoneNumber = document.getElementById('phone-number').value.trim();
        
        // 验证手机号
        const phoneField = document.getElementById('phone-number');
        if (!this.validateField(phoneField)) {
            return;
        }
        
        // 检查倒计时状态
        if (this.smsCountdown > 0) {
            return;
        }
        
        // 显示发送中状态
        const sendBtn = document.getElementById('send-code-btn');
        const originalText = sendBtn.textContent;
        sendBtn.disabled = true;
        sendBtn.textContent = '发送中...';
        
        // 发送验证码请求
        const smsPacket = {
            type: 'send_verification_code',
            data: {
                phone_number: phoneNumber
            }
        };
        
        ws.send(smsPacket);
        
        // 启动倒计时
        this.startSmsCountdown();
    }
    
    // 验证码倒计时
    startSmsCountdown() {
        this.smsCountdown = 60;
        const sendBtn = document.getElementById('send-code-btn');
        
        this.updateSmsButton();
        
        this.smsTimer = setInterval(() => {
            this.smsCountdown--;
            this.updateSmsButton();
            
            if (this.smsCountdown <= 0) {
                clearInterval(this.smsTimer);
                this.smsTimer = null;
            }
        }, 1000);
    }
    
    // 更新验证码按钮状态
    updateSmsButton() {
        const sendBtn = document.getElementById('send-code-btn');
        
        if (this.smsCountdown > 0) {
            sendBtn.disabled = true;
            sendBtn.textContent = `${this.smsCountdown}秒后重发`;
        } else {
            sendBtn.disabled = false;
            sendBtn.textContent = '获取验证码';
        }
    }
    
    // 提交实名认证表单
    submitVerificationForm() {
        // 验证表单
        if (!this.validateForm()) {
            return;
        }
        
        // 显示加载状态
        const submitBtn = document.querySelector('#verification-modal .btn-primary[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = '提交中...';
        
        // 获取表单数据
        const formData = {
            real_name: document.getElementById('real-name').value.trim(),
            id_card: document.getElementById('id-card').value.trim(),
            phone_number: document.getElementById('phone-number').value.trim(),
            verification_code: document.getElementById('verification-code').value.trim(),
            request_id: 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
        };
        
        // 发送认证请求
        const verificationPacket = {
            type: 'submit_verification',
            data: formData
        };
        
        ws.send(verificationPacket);
    }
    
    // 处理模态框关闭
    handleModalClose() {
        if (this.formDataChanged) {
            if (confirm('您的填写内容尚未保存，确定要放弃吗？')) {
                this.closeModal();
            } else {
                return false; // 阻止模态框关闭
            }
        } else {
            this.closeModal();
        }
    }
    
    // 关闭模态框
    closeModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('verification-modal'));
        if (modal) {
            modal.hide();
        }
    }
    
    // 显示服务协议
    showAgreement() {
        app.showToast('《实名认证服务协议》功能开发中...', 'info');
        // 这里可以实现协议弹窗或跳转
    }
    
    // 处理验证码发送响应
    handleSmsResponse(packet) {
        const sendBtn = document.getElementById('send-code-btn');
        if (packet.status === 'success') {
            app.showToast('验证码发送成功，请查收短信', 'success');
        } else {
            // 清除倒计时
            if (this.smsTimer) {
                clearInterval(this.smsTimer);
                this.smsTimer = null;
                this.smsCountdown = 0;
                this.updateSmsButton();
            }
            
            const errorMessage = packet.data?.message || '验证码发送失败，请稍后重试';
            app.showToast(errorMessage, 'error');
        }
    }
    
    // 处理实名认证响应
    handleVerificationResponse(packet) {
        // 恢复提交按钮状态
        const submitBtn = document.querySelector('#verification-modal .btn-primary[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.textContent = '提交认证';
        
        if (packet.status === 'success') {
            app.showToast('实名认证提交成功，正在审核中', 'success');
            this.verificationStatus = {
                status: 1, // 审核中
                realName: document.getElementById('real-name').value.trim(),
                idCard: document.getElementById('id-card').value.trim(),
                phoneNumber: document.getElementById('phone-number').value.trim()
            };
            
            // 保存到本地存储
            app.setLocalStorage('verificationStatus', this.verificationStatus);
            
            // 更新页面显示
            this.updateVerificationStatusDisplay();
            
            // 关闭弹窗
            this.closeModal();
        } else {
            const errorMessage = packet.data?.message || '实名认证提交失败，请稍后重试';
            app.showToast(errorMessage, 'error');
        }
    }
    
    // 处理个人资料刷新响应
    handleProfileRefreshResponse(packet) {
        if (packet.status === 'success') {
            const profileData = packet.data;
            
            // 更新用户信息
            app.setCurrentUser({
                username: profileData.username,
                permission_level: profileData.permission_level
            });
            
            // 更新实名认证状态
            this.verificationStatus = {
                status: profileData.verification_status,
                realName: profileData.real_name,
                idCard: profileData.id_card,
                phoneNumber: profileData.phone_number,
                reason: profileData.verification_reason
            };
            
            // 保存到本地存储
            app.setLocalStorage('verificationStatus', this.verificationStatus);
            
            // 更新页面显示
            this.updateProfileInfo();
            this.updateVerificationStatusDisplay();
        }
    }
    
    // 获取权限等级文本
    getPermissionText(level) {
        switch(level) {
            case 0: return '普通用户';
            case 1: return '基础权限用户';
            case 2: return '数据管理用户';
            case 3: return '搜索源管理用户';
            case 4: return '管理员';
            default: return '未知权限';
        }
    }
}

// 初始化个人资料页面
const profilePage = new ProfilePage();
window.profilePage = profilePage;