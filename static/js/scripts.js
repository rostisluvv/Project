document.addEventListener('DOMContentLoaded', function () {
    let currentSlide = 0;
    const slides = document.querySelectorAll('.carousel img');
    const totalSlides = slides.length;

    // Добавляем обработчик событий для кнопки "next"
    document.getElementById('next').addEventListener('click', function () {
        changeSlide(1);
    });

    // Добавляем обработчик событий для кнопки "prev"
    document.getElementById('prev').addEventListener('click', function () {
        changeSlide(-1);
    });

    // Устанавливаем интервал для автоматического переключения слайдов каждые 5 секунд
    setInterval(function () {
        changeSlide(1);
    }, 5000);

    // Функция для изменения слайда
    function changeSlide(step) {
        slides[currentSlide].classList.remove('active'); // Убираем класс "active" с текущего слайда
        currentSlide = (currentSlide + step + totalSlides) % totalSlides; // Вычисляем следующий слайд с учетом кругового перехода
        slides[currentSlide].classList.add('active'); // Добавляем класс "active" новому слайду
    }
});

// Функция для плавного скроллинга наверх страницы
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Показать кнопку прокрутки наверх при прокрутке страницы
window.addEventListener('scroll', function () {
    var scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (window.scrollY > 300) {
        scrollToTopBtn.style.display = 'block'; // Показываем кнопку, если прокрутили страницу вниз на 300 пикселей
    } else {
        scrollToTopBtn.style.display = 'none'; // Скрываем кнопку, если прокрутка меньше 300 пикселей
    }
});

document.getElementById('search-input').addEventListener('keyup', function () {
    const query = this.value;
    if (query.length > 2) {
        fetch(`/autocomplete/?term=${query}`)
            .then(response => response.json())
            .then(data => {
                const results = document.getElementById('autocomplete-results');
                results.innerHTML = '';
                if (data.length) {
                    data.forEach(item => {
                        const div = document.createElement('div');
                        div.classList.add('autocomplete-item');
                        div.innerText = item;
                        div.addEventListener('click', function () {
                            document.getElementById('search-input').value = this.innerText;
                            results.innerHTML = '';
                        });
                        results.appendChild(div);
                    });
                }
            });
    } else {
        document.getElementById('autocomplete-results').innerHTML = '';
    }
});
