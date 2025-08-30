// Глобальные переменные
let currentStep = 1;
let uploadedPhotos = [];
let formData = {};

// Функции навигации между шагами
function nextStep(step) {
    if (step === undefined) {
        const currentStepElement = document.querySelector('.step:not([style*="display: none"])');
        const currentStepNum = parseInt(currentStepElement.id.replace('step', ''));
        
        if (currentStepNum === 1) {
            const serviceType = document.querySelector('input[name="service_type"]:checked');
            if (!serviceType) {
                showError('Пожалуйста, выберите тип услуги');
                return;
            }
            
            // Показать соответствующую подформу
            const serviceValue = serviceType.value;
            if (serviceValue.includes('Инвестиционные')) {
                showSubStep('investment');
                return;
            } else if (serviceValue.includes('Оценка')) {
                showSubStep('appraisal');
                return;
            } else if (serviceValue.includes('Покупка') || serviceValue.includes('Продажа')) {
                showSubStep('property');
                return;
            } else if (serviceValue.includes('Страховые')) {
                showSubStep('insurance');
                return;
            }
        }
    }
    
    if (validateCurrentStep()) {
        saveCurrentStepData();
        showStep(step);
    }
}

function prevStep(step) {
    showStep(step);
}

function showStep(step) {
    // Скрыть все шаги
    document.querySelectorAll('.step').forEach(s => {
        s.style.display = 'none';
    });
    
    // Показать текущий шаг
    document.getElementById(`step${step}`).style.display = 'block';
    currentStep = step;
    
    // Прокрутить к началу формы
    document.querySelector('.investment-form').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// Функция для показа подшагов
function showSubStep(type) {
    // Скрыть основной шаг 1
    document.getElementById('step1').style.display = 'none';
    
    // Показать соответствующий подшаг
    const subStepId = `step1_${type}`;
    const subStep = document.getElementById(subStepId);
    if (subStep) {
        subStep.style.display = 'block';
        subStep.classList.add('step');
    }
}

// Валидация текущего шага
function validateCurrentStep() {
    const currentStepElement = document.querySelector('.step:not([style*="display: none"])');
    const stepId = currentStepElement.id;
    
    if (stepId === 'step1') {
        const serviceType = document.querySelector('input[name="service_type"]:checked');
        if (!serviceType) {
            showError('Пожалуйста, выберите тип услуги');
            return false;
        }
    } else if (stepId.startsWith('step1_')) {
        // Валидация подшагов
        const type = stepId.replace('step1_', '');
        let fieldName;
        switch(type) {
            case 'investment':
                fieldName = 'direction';
                break;
            case 'appraisal':
                fieldName = 'object_type';
                break;
            case 'property':
                fieldName = 'property_type';
                break;
            case 'insurance':
                fieldName = 'insurance_type';
                break;
        }
        
        const selected = document.querySelector(`input[name="${fieldName}"]:checked`);
        if (!selected) {
            showError('Пожалуйста, сделайте выбор');
            return false;
        }
    } else {
        const stepNum = parseInt(stepId.replace('step', ''));
        switch(stepNum) {
            case 1:
                const direction = document.querySelector('input[name="direction"]:checked');
                if (!direction) {
                    showError('Пожалуйста, выберите направление инвестиций');
                    return false;
                }
                break;
            
        case 2:
            const amount = document.getElementById('amount').value.trim();
            if (!amount) {
                showError('Пожалуйста, укажите сумму инвестиций');
                return false;
            }
            if (!/^\d+$/.test(amount.replace(/\s/g, ''))) {
                showError('Сумма должна содержать только цифры');
                return false;
            }
            break;
            
        case 3:
            const term = document.getElementById('term').value.trim();
            if (!term) {
                showError('Пожалуйста, укажите срок инвестиций');
                return false;
            }
            break;
            
        case 6:
            const contact = document.getElementById('contact').value.trim();
            if (!contact) {
                showError('Пожалуйста, укажите контактную информацию');
                return false;
            }
            break;
        }
    }
    return true;
}

// Сохранение данных текущего шага
function saveCurrentStepData() {
    switch(currentStep) {
        case 1:
            const direction = document.querySelector('input[name="direction"]:checked');
            formData.direction = direction ? direction.value : '';
            break;
            
        case 2:
            formData.amount = document.getElementById('amount').value.trim();
            break;
            
        case 3:
            formData.term = document.getElementById('term').value.trim();
            break;
            
        case 4:
            formData.comment = document.getElementById('comment').value.trim();
            break;
            
        case 5:
            formData.photos = uploadedPhotos;
            break;
            
        case 6:
            formData.contact = document.getElementById('contact').value.trim();
            break;
    }
}

// Обработка загрузки фотографий
function handlePhotoUpload(event) {
    const files = Array.from(event.target.files);
    
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const photoData = {
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    data: e.target.result
                };
                
                uploadedPhotos.push(photoData);
                displayPhotoPreview(photoData, uploadedPhotos.length - 1);
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Очистить input для возможности повторной загрузки
    event.target.value = '';
}

// Отображение превью фотографий
function displayPhotoPreview(photoData, index) {
    const previewContainer = document.getElementById('photoPreview');
    
    const photoItem = document.createElement('div');
    photoItem.className = 'photo-item';
    photoItem.innerHTML = `
        <img src="${photoData.data}" alt="${photoData.name}" title="${photoData.name}">
        <button type="button" class="photo-remove" onclick="removePhoto(${index})" title="Удалить фото">×</button>
    `;
    
    previewContainer.appendChild(photoItem);
}

// Удаление фотографии
function removePhoto(index) {
    uploadedPhotos.splice(index, 1);
    refreshPhotoPreview();
}

// Обновление превью фотографий
function refreshPhotoPreview() {
    const previewContainer = document.getElementById('photoPreview');
    previewContainer.innerHTML = '';
    
    uploadedPhotos.forEach((photo, index) => {
        displayPhotoPreview(photo, index);
    });
}

// Форматирование суммы
function formatAmount(input) {
    let value = input.value.replace(/\D/g, '');
    value = value.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    input.value = value;
}

// Добавить обработчик для форматирования суммы
document.addEventListener('DOMContentLoaded', function() {
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            formatAmount(this);
        });
    }
});

// Показ ошибок
function showError(message) {
    // Удалить предыдущие ошибки
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Создать новое сообщение об ошибке
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        background: #fed7d7;
        border: 1px solid #fc8181;
        color: #c53030;
        padding: 12px;
        border-radius: 8px;
        margin: 15px 0;
        font-weight: 500;
        animation: shake 0.5s ease-in-out;
    `;
    errorDiv.textContent = `⚠️ ${message}`;
    
    // Добавить стили для анимации
    if (!document.querySelector('#errorStyles')) {
        const style = document.createElement('style');
        style.id = 'errorStyles';
        style.textContent = `
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Вставить сообщение перед кнопками текущего шага
    const currentStepElement = document.getElementById(`step${currentStep}`);
    const buttons = currentStepElement.querySelector('.step-buttons') || currentStepElement.querySelector('.btn');
    if (buttons) {
        buttons.parentNode.insertBefore(errorDiv, buttons);
    } else {
        currentStepElement.appendChild(errorDiv);
    }
    
    // Прокрутить к ошибке
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Удалить ошибку через 5 секунд
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

// Показ модального окна успеха
function showSuccessModal() {
    document.getElementById('successModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// Закрытие модального окна
function closeModal() {
    document.getElementById('successModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    
    // Сброс формы
    resetForm();
}

// Сброс формы
function resetForm() {
    currentStep = 1;
    uploadedPhotos = [];
    formData = {};
    
    // Очистить все поля
    document.getElementById('investmentForm').reset();
    document.getElementById('photoPreview').innerHTML = '';
    
    // Показать первый шаг
    showStep(1);
    
    // Прокрутить к началу
    document.querySelector('.header').scrollIntoView({ behavior: 'smooth' });
}

function collectFormData() {
    const serviceType = document.querySelector('input[name="service_type"]:checked')?.value || '';
    
    const formData = {
        service_type: serviceType,
        direction: document.querySelector('input[name="direction"]:checked')?.value || '',
        object_type: document.querySelector('input[name="object_type"]:checked')?.value || '',
        property_type: document.querySelector('input[name="property_type"]:checked')?.value || '',
        insurance_type: document.querySelector('input[name="insurance_type"]:checked')?.value || '',
        amount: document.getElementById('amount')?.value || '',
        term: document.getElementById('term')?.value || '',
        comment: document.getElementById('comment')?.value || '',
        contact: document.getElementById('contact')?.value || '',
        photos: uploadedPhotos
    };
    
    return formData;
}

function formatFormDataForSubmission(formData) {
    let message = `📋 Новая заявка:\n\n`;
    message += `🎯 Тип услуги: ${formData.service_type}\n`;
    
    // Добавляем специфичные поля в зависимости от типа услуги
    if (formData.direction) {
        message += `💼 Направление инвестиций: ${formData.direction}\n`;
    }
    if (formData.object_type) {
        message += `🏠 Тип объекта для оценки: ${formData.object_type}\n`;
    }
    if (formData.property_type) {
        message += `🏡 Тип недвижимости: ${formData.property_type}\n`;
    }
    if (formData.insurance_type) {
        message += `🛡️ Тип страхования: ${formData.insurance_type}\n`;
    }
    
    if (formData.amount) {
        message += `💰 Сумма: ${formData.amount}\n`;
    }
    if (formData.term) {
        message += `📅 Срок: ${formData.term}\n`;
    }
    
    if (formData.comment) {
        message += `💬 Дополнительные комментарии: ${formData.comment}\n`;
    }
    
    if (formData.photos && formData.photos.length > 0) {
        message += `📸 Прикреплено фотографий: ${formData.photos.length}\n`;
    }
    
    message += `📞 Контактная информация: ${formData.contact}\n`;
    message += `\n⏰ Время подачи заявки: ${new Date().toLocaleString('ru-RU')}`;
    
    return message;
}

// Отправка формы
function submitForm() {
    // Сохранить данные последнего шага
    saveCurrentStepData();
    
    // Собрать все данные формы
    const collectedData = collectFormData();
    
    // Подготовить данные для отправки
    const submissionData = {
        service_type: collectedData.service_type || 'Не указано',
        direction: collectedData.direction || 'Не указано',
        object_type: collectedData.object_type || 'Не указано',
        property_type: collectedData.property_type || 'Не указано',
        insurance_type: collectedData.insurance_type || 'Не указано',
        amount: collectedData.amount || 'Не указано',
        term: collectedData.term || 'Не указано',
        comment: collectedData.comment || 'Нет комментариев',
        contact: collectedData.contact || 'Не указано',
        photos: uploadedPhotos.length,
        timestamp: new Date().toLocaleString('ru-RU'),
        userAgent: navigator.userAgent
    };
    
    // Симуляция отправки данных
    console.log('Отправка заявки:', submissionData);
    
    // В реальном приложении здесь был бы AJAX запрос
    // Например:
    // fetch('/api/submit-application', {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify(submissionData)
    // })
    // .then(response => response.json())
    // .then(data => {
    //     if (data.success) {
    //         showSuccessModal();
    //     } else {
    //         showError('Произошла ошибка при отправке заявки. Попробуйте еще раз.');
    //     }
    // })
    // .catch(error => {
    //     showError('Произошла ошибка при отправке заявки. Проверьте подключение к интернету.');
    // });
    
    // Для демонстрации показываем успешное окно
    setTimeout(() => {
        showSuccessModal();
    }, 1000);
    
    // Показать индикатор загрузки
    const submitButton = document.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = '⏳ Отправляем...';
    submitButton.disabled = true;
    
    setTimeout(() => {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }, 1000);
}

// Обработчик отправки формы

// Обработчик отправки формы
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('investmentForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateCurrentStep()) {
            submitForm();
        }
    });
    
    // Обработчик для закрытия модального окна по клику вне его
    document.getElementById('successModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
    
    // Обработчик для клавиши Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('successModal');
            if (modal.style.display === 'flex') {
                closeModal();
            }
        }
    });
    
    // Обработка кликов по ссылкам-опциям
    document.addEventListener('click', function(e) {
        const optionLink = e.target.closest('.option-link');
        if (optionLink) {
            e.preventDefault();
            const botType = optionLink.getAttribute('data-bot');
            redirectToTelegramBot(botType);
        }
    });
    
    // Автофокус на первом элементе формы
    const firstRadio = document.querySelector('input[name="direction"]');
    if (firstRadio) {
        firstRadio.focus();
    }
});

// Функция перенаправления к Telegram-боту
function redirectToTelegramBot(botType) {
    // Ссылки на конкретные боты с презентабельными названиями
    const botLinks = {
        'investment': 'https://t.me/tda_anketa_invBot?start=investicii',
        'appraisal': 'https://t.me/tda_anketa_OceBot?start=ocenka',
        'property_buy': 'https://t.me/tda_anketa_poBot?start=pokupka',
        'property_sell': 'https://t.me/tda_anketa_pBot?start=prodazha',
        'insurance_osago': 'https://t.me/tda_anketa_StrBot?start=osago',
        'insurance_mortgage': 'https://t.me/tda_anketa_StrBot?start=ipoteka',
        'insurance_property': 'https://t.me/tda_anketa_StrBot?start=imushhestvo',
        'insurance_cargo': 'https://t.me/tda_anketa_StrBot?start=gruzy',
        'insurance_tick': 'https://t.me/tda_anketa_StrBot?start=kleshhi',
        'insurance_accident': 'https://t.me/tda_anketa_StrBot?start=neschastnyj_sluchaj',
        'insurance_unemployment': 'https://t.me/tda_anketa_StrBot?start=bezrabotica'
    };

    // Презентабельные названия ботов
    const botNames = {
        'investment': '💰 ПроИнвест Консультант',
        'appraisal': '🏠 Эксперт Оценки',
        'property_buy': '🛒 Помощник Покупателя',
        'property_sell': '💼 Консультант Продавца',
        'insurance_osago': '🚗 Страховой Эксперт',
        'insurance_mortgage': '🏠 Страховой Эксперт',
        'insurance_property': '🏡 Страховой Эксперт',
        'insurance_cargo': '📦 Страховой Эксперт',
        'insurance_tick': '🦟 Страховой Эксперт',
        'insurance_accident': '⚕️ Страховой Эксперт',
        'insurance_unemployment': '💼 Страховой Эксперт'
    };

    const botUrl = botLinks[botType];
    const botName = botNames[botType];
    
    if (botUrl && botName) {
        // Показываем уведомление с названием бота
        alert(`Переходим к боту "${botName}" для получения персональной консультации...`);
        // Открываем ссылку в новой вкладке
        window.open(botUrl, '_blank');
    } else {
        alert('Ссылка на бот пока не настроена. Пожалуйста, свяжитесь с нами для получения ссылки.');
    }
}

// Функции для улучшения UX
function addInputAnimations() {
    const inputs = document.querySelectorAll('input[type="text"], textarea');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    addInputAnimations();
    
    // Добавить плавную прокрутку для всех ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Добавить обработчики для радиокнопок
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            // Убрать выделение с других опций
            document.querySelectorAll('.option').forEach(option => {
                option.classList.remove('selected');
            });
            
            // Выделить выбранную опцию
            this.closest('.option').classList.add('selected');
        });
    });
});

// Функция для отслеживания прогресса
function updateProgress() {
    const totalSteps = 6;
    const progress = (currentStep / totalSteps) * 100;
    
    // Можно добавить индикатор прогресса
    console.log(`Прогресс: ${Math.round(progress)}%`);
}

// Вызывать при смене шага
function showStep(step) {
    document.querySelectorAll('.step').forEach(s => {
        s.style.display = 'none';
    });
    
    document.getElementById(`step${step}`).style.display = 'block';
    currentStep = step;
    updateProgress();
    
    document.querySelector('.investment-form').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}