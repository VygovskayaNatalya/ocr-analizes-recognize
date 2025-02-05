 // Обработчик для обновления сообщения о Tesseract и GPU
 function updateTesseractInfo() {
    const tesseractInfo = document.getElementById("tesseractInfo");
    const useGpu = document.getElementById("useGpu").checked;
    const isTesseractSelected = document.getElementById("tesseract").checked;

    if (isTesseractSelected && useGpu) {
        tesseractInfo.style.display = "block";
    } else {
        tesseractInfo.style.display = "none";
    }
}

// Добавляем обработчики событий для drag and drop
const dropZone = document.getElementById("dropZone");
const imageInput = document.getElementById("imageInput");

dropZone.addEventListener("dragover", function(event) {
    event.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", function(event) {
    event.preventDefault();
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", function(event) {
    event.preventDefault();
    dropZone.classList.remove("dragover");
    
    const file = event.dataTransfer.files[0];
    imageInput.files = event.dataTransfer.files;
    previewImage(file);
    document.getElementById("recognizeButton").disabled = false;
});

imageInput.addEventListener("change", function() {
    const file = this.files[0];
    previewImage(file);
    document.getElementById("recognizeButton").disabled = false;
});

function previewImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const imagePreview = document.getElementById("imagePreview");
        imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview" />`;
    };
    reader.readAsDataURL(file);
}

// Показывает спиннер
function showSpinner() {
    document.getElementById('spinner').classList.remove('hidden');
}

// Скрывает спиннер
function hideSpinner() {
    document.getElementById('spinner').classList.add('hidden');
}

// Отправка изображения на сервер
async function uploadImage() {
    const fileInput = document.getElementById("imageInput");
    const file = fileInput.files[0];  // Получаем файл из input

    // Проверяем, что файл выбран
    if (!file) {
        alert("Пожалуйста, выберите изображение.");
        return;
    }

    const engines = [];
    if (document.getElementById("easyocr").checked) engines.push("easyocr");
    if (document.getElementById("tesseract").checked) engines.push("tesseract");
    if (document.getElementById("paddleocr").checked) engines.push("paddleocr");

    const useGpu = document.getElementById("useGpu").checked;

    // Преобразуем файл в строку Base64
    const reader = new FileReader();
    reader.onloadend = async function() {
        const base64Image = reader.result.split(',')[1];  // Получаем только Base64 часть
        const requestData = {
            request: {
                file: base64Image,
                engines: engines,
                use_gpu: useGpu
            }
        };

        showSpinner(); // Показываем спиннер

        // Отправка данных на сервер
        const response = await fetch("http://localhost:8000/ocr", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                file: base64Image,
                engines: engines,
                use_gpu: useGpu
            })
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById("outputText").innerHTML = data.results.map(result => `
                <div>
                    <h3 style="margin: 0; color: #333; font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 8px;">
                        Движок: ${result.engine}
                    </h3>
                    <p>
                        ${result.text || `<b>Ошибка:</b> ${result.error}`}
                    </p>
                </div>
            `).join("");
        } else {
            alert("Ошибка при распознавании текста");
        }
        hideSpinner();
    };

    reader.readAsDataURL(file);  // Чтение файла как Base64
}
// Слушаем изменение флага использования GPU
document.getElementById("useGpu").addEventListener("change", updateTesseractInfo);
// Слушаем изменение флага Tesseract
document.getElementById("tesseract").addEventListener("change", updateTesseractInfo);

// Инициализируем начальное состояние
updateTesseractInfo();

async function analyzeText() {  
    const ocrText = document.querySelector("#outputText").textContent;  
    console.log("Sending text:", ocrText);  
    

    try {  
        const response = await fetch("http://127.0.0.1:8000/structure_analysis", {  
            method: "POST",  
            headers: {  
                "Content-Type": "application/json"  
            },  
            body: JSON.stringify({ text: ocrText })  
        });  

        // Проверка успешного выполнения запроса  
        if (!response.ok) {  
            throw new Error(`HTTP error! status: ${response.status}`);  
        }  

        const data = await response.json();  
        console.log("Received data:", data);  
        localStorage.setItem("analysisTable", data.structured_analysis);  
        
        // Открытие новой страницы  
        window.open("http://127.0.0.1:8000/analysis", "_blank");  
    } catch (error) {  
        console.error("Error during analysis:", error);  
    }  
    hideSpinner(); // Скрываем спиннер
}
