// Page Navigation Functions
function showSignIn() {
    document.getElementById('signInPage').classList.add('active');
    resetForms();
}

function showSignUp() {
    document.getElementById('signInPage').classList.remove('active');
    resetForms();
}

// Reset Forms Function
function resetForms() {
    document.getElementById('signInForm').reset();
    document.getElementById('signUpForm').reset();
    document.getElementById('signInOtpSection').style.display = 'none';
    document.getElementById('signUpOtpSection').style.display = 'none';
    document.getElementById('signUpStep1').style.display = 'block';
    document.getElementById('signInBtn').textContent = 'Send OTP';
    document.getElementById('signUpBtn').textContent = 'Send OTP';
    clearOtpInputs();
    hideMessages();
}

// Message Handling Functions
function hideMessages() {
    document.querySelectorAll('.success-message, .error-message').forEach(msg => {
        msg.style.display = 'none';
    });
}

function showMessage(elementId) {
    hideMessages();
    const element = document.getElementById(elementId);
    element.style.display = 'block';
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

// Indian Phone Number Formatting Function
function formatIndianPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    // Limit to 10 digits for Indian numbers
    value = value.substring(0, 10);
    
    // Format as XXXXX XXXXX (common Indian format)
    if (value.length > 5) {
        value = value.substring(0, 5) + ' ' + value.substring(5);
    }
    
    input.value = value;
}

// Validate Indian Phone Number
function validateIndianPhoneNumber(phoneNumber) {
    // Remove all non-digit characters
    const cleanNumber = phoneNumber.replace(/\D/g, '');
    
    // Indian mobile numbers should be 10 digits and typically start with 6, 7, 8, or 9
    const indianMobileRegex = /^[6-9]\d{9}$/;
    
    return indianMobileRegex.test(cleanNumber);
}

// Add event listeners for phone number formatting
document.getElementById('signInPhone').addEventListener('input', function() {
    formatIndianPhoneNumber(this);
});

document.getElementById('signUpPhone').addEventListener('input', function() {
    formatIndianPhoneNumber(this);
});

// OTP Input Handling Function
function setupOtpInputs(className = 'otp-input') {
    const inputs = document.querySelectorAll(`.${className}`);
    
    inputs.forEach((input, index) => {
        // Handle input event
        input.addEventListener('input', function() {
            // Only allow digits
            this.value = this.value.replace(/\D/g, '');
            
            // Move to next input if current has value
            if (this.value.length === 1 && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }
        });

        // Handle backspace
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && this.value === '' && index > 0) {
                inputs[index - 1].focus();
            }
        });

        // Handle paste event for OTP
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            const pasteData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
            
            for (let i = 0; i < pasteData.length && i < inputs.length; i++) {
                inputs[i].value = pasteData[i];
            }
            
            // Focus on the last filled input or the next empty one
            const lastFilledIndex = Math.min(pasteData.length - 1, inputs.length - 1);
            inputs[lastFilledIndex].focus();
        });
    });
}

// Initialize OTP inputs
setupOtpInputs('otp-input');
setupOtpInputs('signup-otp');

// Clear OTP Inputs Function
function clearOtpInputs() {
    document.querySelectorAll('.otp-input, .signup-otp').forEach(input => {
        input.value = '';
    });
}

// Timer Functionality
function startTimer(timerId, callback) {
    let timeLeft = 30;
    const timerElement = document.getElementById(timerId);
    
    const interval = setInterval(() => {
        timeLeft--;
        timerElement.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            clearInterval(interval);
            if (callback) {
                callback();
            }
        }
    }, 1000);
    
    return interval;
}

// Sign In Form Handler
document.getElementById('signInForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const phoneInput = document.getElementById('signInPhone');
    const otpSection = document.getElementById('signInOtpSection');
    const phoneSection = document.getElementById('phoneSection');
    const btn = document.getElementById('signInBtn');
    
    if (otpSection.style.display === 'none') {
        // Send OTP Phase
        if (!validateIndianPhoneNumber(phoneInput.value)) {
            showMessage('signInError');
            return;
        }
        
        // Hide phone section and show OTP section
        phoneSection.style.display = 'none';
        otpSection.style.display = 'block';
        btn.textContent = 'Verify & Sign In';
        
        // Start timer for OTP resend
        startTimer('signInTimer', function() {
            // Enable resend OTP functionality here
            console.log('OTP can be resent now');
        });
        
        // Simulate OTP sent (In production, make API call here)
        console.log('OTP sent to: +91 ' + phoneInput.value);
        
        // Focus on first OTP input
        document.querySelector('#signInOtpSection .otp-input').focus();
    } else {
        // Verify OTP Phase
        const otpInputs = document.querySelectorAll('#signInOtpSection .otp-input');
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        
        if (otp.length === 6) {
            // In production, verify OTP with backend API
            console.log('Verifying OTP:', otp);
            
            // Simulate successful verification
            showMessage('signInSuccess');
            
            setTimeout(() => {
                console.log('User signed in successfully');
                // In production, redirect to dashboard or store auth token
                // window.location.href = '/dashboard';
            }, 2000);
        } else {
            showMessage('signInError');
        }
    }
});

// Sign Up Form Handler
document.getElementById('signUpForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const fullName = document.getElementById('fullName');
    const email = document.getElementById('email');
    const phoneInput = document.getElementById('signUpPhone');
    const terms = document.getElementById('terms');
    const otpSection = document.getElementById('signUpOtpSection');
    const step1 = document.getElementById('signUpStep1');
    const btn = document.getElementById('signUpBtn');
    
    if (otpSection.style.display === 'none') {
        // Validate and Send OTP Phase
        
        // Validate full name
        if (!fullName.value.trim() || fullName.value.trim().length < 2) {
            showMessage('signUpError');
            fullName.focus();
            return;
        }
        
        // Validate email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value)) {
            showMessage('signUpError');
            email.focus();
            return;
        }
        
        // Validate phone number
        if (!validateIndianPhoneNumber(phoneInput.value)) {
            showMessage('signUpError');
            phoneInput.focus();
            return;
        }
        
        if (!terms.checked) {
            showMessage('signUpError');
            return;
        }
        
        step1.style.display = 'none';
        otpSection.style.display = 'block';
        btn.textContent = 'Verify & Create Account';

        signupVerifyOtp.addEventListener('click', () => {
        const phone = signupPhone.value.trim();
        const otp = signupOtpInput.value.trim();
        
        if (otpStore[phone] === otp) {
            // Store authentication state
            localStorage.setItem('signedIn', 'true');
            localStorage.setItem('userPhone', phone);
            localStorage.setItem('signupCompleted', 'true');
            
            // Update button text and show success message
            signupVerifyOtp.textContent = 'Verify & Create Account';
            signupMessage.style.color = 'hsl(var(--success))';
            signupMessage.textContent = 'Phone verified! Redirecting to complete registration...';
            
            // Redirect to profile.html after a brief delay
            setTimeout(() => {
            toggleModal(signupModal, false);
            window.location.href = 'profile.html';
            }, 1500);
        } else {
            signupMessage.style.color = 'hsl(var(--destructive))';
            signupMessage.textContent = 'Invalid OTP. Please try again.';
        }
        });

        
        // Start timer for OTP resend
        startTimer('signUpTimer', function() {
            // Enable resend OTP functionality here
            console.log('OTP can be resent now');
        });
        
        // Simulate OTP sent (In production, make API call here)
        console.log('OTP sent to: +91 ' + phoneInput.value);
        
        // Store form data temporarily (In production, handle this securely)
        window.tempSignUpData = {
            name: fullName.value,
            email: email.value,
            phone: phoneInput.value
        };
        
        // Focus on first OTP input
        document.querySelector('#signUpOtpSection .signup-otp').focus();
    } else {
        // Verify OTP and Create Account Phase
        const otpInputs = document.querySelectorAll('#signUpOtpSection .signup-otp');
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        
        if (otp.length === 6) {
            // In production, verify OTP and create account via API
            console.log('Creating account with OTP:', otp);
            console.log('User data:', window.tempSignUpData);
            
            // Simulate successful account creation
            showMessage('signUpSuccess');
            
            setTimeout(() => {
                console.log('Account created successfully');
                // Clear temporary data
                delete window.tempSignUpData;
                // Switch to sign in page
                showSignIn();
            }, 2000);
        } else {
            showMessage('signUpError');
        }
    }
});

// Add resend OTP functionality
function resendOTP(type) {
    const timerId = type === 'signin' ? 'signInTimer' : 'signUpTimer';
    const phoneInput = type === 'signin' ? 
        document.getElementById('signInPhone') : 
        document.getElementById('signUpPhone');
    
    console.log('Resending OTP to: +91 ' + phoneInput.value);
    
    // Reset timer
    startTimer(timerId);
    
    // Clear existing OTP inputs
    if (type === 'signin') {
        document.querySelectorAll('#signInOtpSection .otp-input').forEach(input => {
            input.value = '';
        });
    } else {
        document.querySelectorAll('#signUpOtpSection .signup-otp').forEach(input => {
            input.value = '';
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Phone Authentication System Initialized');
    console.log('Country Code: +91 (India)');
});