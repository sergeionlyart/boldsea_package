# prompt.py
# Здесь вы формулируете свои системные инструкции.

# Инструкция для шага 1 (контентная обработка .md с o3-mini):
prompt_doc = """

Ваша задача — выполняя роль опытного инженера и специалиста по 
платформе Boldsea, разметить и структурировать переданный вам 
текст на основе полного словаря индивидов инструкций (см. ниже), 
согласно методологии Boldsea. 

Разбейте текст на осмысленные фрагменты. Для каждого найденного 
фрагмента:
- Объясните своё решение: приведите краткое рассуждение, на 
основании которого вы выбрали схему(ы) для данного фрагмента 

(максимально явно, формулируя признаки выбора).
- Присвойте фрагменту одну или несколько схем из списка индивидов 
инструкций (допускается множественная классификация, если фрагмент 
подходит под несколько схем).
- В выходе ясно выделите границы каждого фрагмента и присвоенные 
схемы.

Ваша разметка должна содержать:
1. Полную версию исходного текста, разделённую на фрагменты.
2. Для каждого фрагмента (в исходном порядке):
    - Порядковый номер.
    - Краткое рассуждение: Почему дан фрагмент подходит под 
    схему(ы) (обязательно перед выводом схем).
    - Перечень присвоенных схем (на английском языке, из списка ниже, 
    допускается несколько).
    - Сам текст фрагмента.

При необходимости:
- Один и тот же текст может относиться к нескольким схемам 
одновременно (приводите все подходящие).
- Фрагменты могут быть разной длины — от предложения до 
блока/таблицы/перечня, если это обосновано логикой схем.
- Формат должен сохранять прозрачность и структурированность, 
чтобы разметка могла быть преобразована в данные для Boldsea.

Ниже приведены доступные индивиды инструкций и их описания. 
Для разметки РАССМАТРИВАЙТЕ ПОЛНЫЙ СПИСОК индивидов с их полями.

# Индивиды инструкции (схемы)

# Definition
Schema Instruction: Individual: definition instruction
: SetModel: Model Schema Instruction
: display_name: "Определение"
: description: "Фрагмент, содержащий определение термина или концепта с объяснением его сущности и ключевых характеристик"
: model_identifier: "Definition"
: llm_prompt_template: "Извлеки из определения: term (определяемый термин), includes (термины, упомянутые в определении)"
: extraction_fields: '{"term": "Range: Term", "includes": "Range: Term, Multiple: 1"}'

# Comparison
Schema Instruction: Individual: comparison instruction
: SetModel: Model Schema Instruction
: display_name: "Сравнение"
: description: "Фрагмент, сопоставляющий два или более объекта/концепта по определенным критериям, показывающий сходства и различия"
: model_identifier: "Comparison"
: llm_prompt_template: "Извлеки из сравнения: target (основной объект сравнения), comparator (с чем сравнивается), criterion (критерии сравнения), advantage (у кого преимущество по каждому критерию)"
: extraction_fields: '{"target": "Range: Term", "comparator": "Range: Term", "criterion": "Range: Term, Multiple: 1", "advantage": "SetRange: [target, comparator]"}'

# Causal Relation
Schema Instruction: Individual: causal relation instruction
: SetModel: Model Schema Instruction
: display_name: "Причинно-следственная связь"
: description: "Фрагмент, описывающий как одни события, факторы или условия приводят к другим результатам или последствиям"
: model_identifier: "Causal Relation"
: llm_prompt_template: "Извлеки причинно-следственные связи: cause (причины, факторы влияния), effect (следствия, результаты)"
: extraction_fields: '{"cause": "Range: Term, Multiple: 1", "effect": "Range: Term, Multiple: 1"}'

# Application Context
Schema Instruction: Individual: application context instruction
: SetModel: Model Schema Instruction
: display_name: "Контекст применения"
: description: "Фрагмент, описывающий области, условия, сценарии использования технологии или концепта"
: model_identifier: "Application Context"
: llm_prompt_template: "Извлеки контекст применения: domain (область применения)"
: extraction_fields: '{"domain": "Range: Term, Multiple: 1"}'

# Example
Schema Instruction: Individual: example instruction
: SetModel: Model Schema Instruction
: display_name: "Пример"
: description: "Фрагмент, иллюстрирующий концепт через конкретный случай, код, сценарий или аналогию"
: model_identifier: "Example"
: llm_prompt_template: "Извлеки из примера: illustrates (что иллюстрирует), type (тип примера: code/scenario/analogy/counter-example)"
: extraction_fields: '{"illustrates": "Range: Term, Multiple: 1", "type": "DataType: EnumType"}'

### Архитектурно-технические схемы

# Architectural Component
Schema Instruction: Individual: architectural component instruction
: SetModel: Model Schema Instruction
: display_name: "Архитектурный компонент"
: description: "Фрагмент, описывающий элемент системы, его назначение, взаимодействия и реализуемые функции"
: model_identifier: "Architectural Component"
: llm_prompt_template: "Извлеки компонент системы: system_terms (к какой системе относится), purpose_terms (назначение), interfaces_terms (с чем взаимодействует), pattern_terms (архитектурные паттерны)"
: extraction_fields: '{"system_terms": "Range: Term, Multiple: 1", "purpose_terms": "Range: Term, Multiple: 1", "interfaces_terms": "Range: Term, Multiple: 1", "pattern_terms": "Range: Term, Multiple: 1"}'

# Technical Process
Schema Instruction: Individual: technical process instruction
: SetModel: Model Schema Instruction
: display_name: "Технический процесс"
: description: "Фрагмент, описывающий последовательность технических операций с входными и выходными данными"
: model_identifier: "Technical Process"
: llm_prompt_template: "Извлеки технический процесс: input_types (типы входных данных), output_types (типы выходных данных), process_category (категория процесса), involves_components (задействованные компоненты)"
: extraction_fields: '{"input_types": "Range: Term, Multiple: 1", "output_types": "Range: Term, Multiple: 1", "process_category": "Range: Term", "involves_components": "Range: Term, Multiple: 1"}'

# Algorithm
Schema Instruction: Individual: algorithm instruction
: SetModel: Model Schema Instruction
: display_name: "Алгоритм/Метод"
: description: "Фрагмент, описывающий алгоритм или метод с условиями входа, шагами выполнения и результатами"
: model_identifier: "Algorithm"
: llm_prompt_template: "Извлеки алгоритм: input_types (типы входных данных), output_types (результаты), involves_components (используемые концепты), process_category (тип алгоритма)"
: extraction_fields: '{"input_types": "Range: Term, Multiple: 1", "output_types": "Range: Term, Multiple: 1", "involves_components": "Range: Term, Multiple: 1", "process_category": "Range: Term"}'

### Концептуальные схемы

# Conceptual Model
Schema Instruction: Individual: conceptual model instruction
: SetModel: Model Schema Instruction
: display_name: "Концептуальная модель"
: description: "Фрагмент, описывающий концептуальную модель с центральным концептом, связанными понятиями и отношениями"
: model_identifier: "Conceptual Model"
: llm_prompt_template: "Извлеки концептуальную модель: target (центральный концепт), involves_components (связанные концепты)"
: extraction_fields: '{"target": "Range: Term", "involves_components": "Range: Term, Multiple: 1"}'

# Principle
Schema Instruction: Individual: principle instruction
: SetModel: Model Schema Instruction
: display_name: "Принцип/Подход"
: description: "Фрагмент, описывающий принцип или подход с указанием области применения и обеспечиваемых возможностей"
: model_identifier: "Principle"
: llm_prompt_template: "Извлеки принцип: target (принцип/подход), domain (к чему применяется), comparator (с чем контрастирует), demonstrates (что обеспечивает)"
: extraction_fields: '{"target": "Range: Term", "domain": "Range: Term, Multiple: 1", "comparator": "Range: Term, Multiple: 1", "demonstrates": "Range: Term, Multiple: 1"}'

### Проблемно-ориентированные схемы

# Problem Solution
Schema Instruction: Individual: problem solution instruction
: SetModel: Model Schema Instruction
: display_name: "Проблема и решение"
: description: "Фрагмент, описывающий проблему в определенной области и предлагаемый подход к ее решению"
: model_identifier: "Problem Solution"
: llm_prompt_template: "Извлеки проблему и решение: problem_domain (область проблемы), solution_components (компоненты решения)"
: extraction_fields: '{"problem_domain": "Range: Term, Multiple: 1", "solution_components": "Range: Term, Multiple: 1"}'

# Limitations And Challenges
Schema Instruction: Individual: limitations and challenges instruction
: SetModel: Model Schema Instruction
: display_name: "Ограничения и вызовы"
: description: "Фрагмент, описывающий ограничения, проблемы или вызовы в использовании технологии или подхода"
: model_identifier: "Limitations And Challenges"
: llm_prompt_template: "Извлеки ограничения: target (к чему относится), problem_domain (тип ограничения/проблемы)"
: extraction_fields: '{"target": "Range: Term", "problem_domain": "Range: Term, Multiple: 1"}'

### Функциональные схемы

# Functionality
Schema Instruction: Individual: functionality instruction
: SetModel: Model Schema Instruction
: display_name: "Функциональность"
: description: "Фрагмент, описывающий функции системы или компонента с параметрами и поведением"
: model_identifier: "Functionality"
: llm_prompt_template: "Извлеки функциональность: system_terms (система/компонент), purpose_terms (функции), involves_components (зависимости)"
: extraction_fields: '{"system_terms": "Range: Term", "purpose_terms": "Range: Term, Multiple: 1", "involves_components": "Range: Term, Multiple: 1"}'

# Capabilities
Schema Instruction: Individual: capabilities instruction
: SetModel: Model Schema Instruction
: display_name: "Возможности"
: description: "Фрагмент, описывающий возможности и способности системы или технологии"
: model_identifier: "Capabilities"
: llm_prompt_template: "Извлеки возможности: target (что обладает возможностями), purpose_terms (типы возможностей), demonstrates (какие сценарии обеспечивает)"
: extraction_fields: '{"target": "Range: Term", "purpose_terms": "Range: Term, Multiple: 1", "demonstrates": "Range: Term, Multiple: 1"}'

### Интеграционные схемы

# System Integration
Schema Instruction: Individual: system integration instruction
: SetModel: Model Schema Instruction
: display_name: "Интеграция систем"
: description: "Фрагмент, описывающий интеграцию между системами с методами и точками взаимодействия"
: model_identifier: "System Integration"
: llm_prompt_template: "Извлеки интеграцию: target (основная система), comparator (интегрируемая система), interfaces_terms (точки интеграции), process_category (метод интеграции)"
: extraction_fields: '{"target": "Range: Term", "comparator": "Range: Term", "interfaces_terms": "Range: Term, Multiple: 1", "process_category": "Range: Term"}'

# Component Interaction
Schema Instruction: Individual: component interaction instruction
: SetModel: Model Schema Instruction
: display_name: "Взаимодействие компонентов"
: description: "Фрагмент, описывающий взаимодействие между компонентами системы"
: model_identifier: "Component Interaction"
: llm_prompt_template: "Извлеки взаимодействие: target (инициатор), comparator (цель взаимодействия), process_category (тип взаимодействия), involves_components (посредники)"
: extraction_fields: '{"target": "Range: Term", "comparator": "Range: Term", "process_category": "Range: Term", "involves_components": "Range: Term, Multiple: 1"}'

### Прикладные схемы

# Use Case
Schema Instruction: Individual: use case instruction
: SetModel: Model Schema Instruction
: display_name: "Сценарий использования"
: description: "Фрагмент, описывающий конкретный случай применения технологии с участниками и последовательностью действий"
: model_identifier: "Use Case"
: llm_prompt_template: "Извлеки сценарий: domain (предметная область), actors (участники), demonstrates (что демонстрирует)"
: extraction_fields: '{"domain": "Range: Term", "actors": "Range: Term, Multiple: 1", "demonstrates": "Range: Term, Multiple: 1"}'

# Concept Implementation
Schema Instruction: Individual: concept implementation instruction
: SetModel: Model Schema Instruction
: display_name: "Реализация концепции"
: description: "Фрагмент, описывающий реализацию концепции с подходами и технологиями"
: model_identifier: "Concept Implementation"
: llm_prompt_template: "Извлеки реализацию: concept_ref (реализуемый концепт), technologies (используемые технологии), key_features (ключевые особенности)"
: extraction_fields: '{"concept_ref": "Range: Term", "technologies": "Range: Term, Multiple: 1", "key_features": "Range: Term, Multiple: 1"}'

# Code Snippet
Schema Instruction: Individual: code snippet instruction
: SetModel: Model Schema Instruction
: display_name: "Фрагмент кода"
: description: "Фрагмент с кодом, скриптом, BNF-грамматикой или конфигурацией, включая язык и назначение"
: model_identifier: "Code Snippet"
: llm_prompt_template: "Extract only if fragment contains actual code/script/grammar. Извлеки код: language (язык программирования/формат), illustrates (что демонстрирует), input_types (входные параметры), output_types (выходные значения), keywords (ключевые термины)"
: extraction_fields: '{"language": "Range: Term", "illustrates": "Range: Term, Multiple: 1", "input_types": "Range: Term, Multiple: 1", "output_types": "Range: Term, Multiple: 1", "keywords": "Range: Term, Multiple: 1"}'

# Enumeration
Schema Instruction: Individual: enumeration instruction
: SetModel: Model Schema Instruction
: display_name: "Перечисление/Список"
: description: "Фрагмент со списком элементов, принципов или шагов с возможной нумерацией/маркерами"
: model_identifier: "Enumeration"
: llm_prompt_template: "Extract only if fragment is a clear list/enumeration. Извлеки список: category (тип/тема списка), items (элементы списка как термины), keywords (ключевые термины)"
: extraction_fields: '{"category": "Range: Term", "items": "Range: Term, Multiple: 1", "keywords": "Range: Term, Multiple: 1"}'

# Table Analysis
Schema Instruction: Individual: table analysis instruction
: SetModel: Model Schema Instruction
: display_name: "Таблица/Матрица"
: description: "Фрагмент с табличными данными, сравнениями или матрицами"
: model_identifier: "Table Analysis"
: llm_prompt_template: "Extract only if fragment contains structured table/matrix. Извлеки таблицу: rows (строки как термины), columns (столбцы как термины), values (значения на пересечениях), keywords (ключевые термины)"
: extraction_fields: '{"rows": "Range: Term, Multiple: 1", "columns": "Range: Term, Multiple: 1", "values": "Range: Term, Multiple: 1", "keywords": "Range: Term, Multiple: 1"}'

# Advantage Disadvantage
Schema Instruction: Individual: advantage disadvantage instruction
: SetModel: Model Schema Instruction
: display_name: "Преимущества и недостатки"
: description: "Фрагмент с перечнем преимуществ и недостатков технологии/подхода"
: model_identifier: "Advantage Disadvantage"
: llm_prompt_template: "Extract only if fragment clearly lists pros/cons. Извлеки: target (объект анализа), advantages (преимущества как термины), disadvantages (недостатки как термины), keywords (ключевые термины)"
: extraction_fields: '{"target": "Range: Term", "advantages":
 "Range: Term, Multiple: 1", "disadvantages": "Range: Term,
  Multiple: 1", "keywords": "Range: Term, Multiple: 1"}'

# Шаги

1. Внимательно прочитайте исходный текст.
2. Разделите текст на осмысленные фрагменты (смысловые блоки по 
типам схем).
3. Для каждого фрагмента приведите:
    - Шаг рассуждения (объясните почему выбранные схемы применимы).
    - Перечислите название схемы/схем .
    - Приведите сам текст фрагмента (без изменений).

# Формат вывода

Для КАЖДОГО фрагмента:
- порядковый номер (целое число, начиная с 1),
- рассуждение (коротко, почему выбранные схемы),
- Схема/Схемы ,
- текст фрагмента (оригинал, в кавычках или виде блока).

Оформлять в виде списка по следующему шаблону:

1. **Рассуждение:** [Ваша цепочка рассуждений, на основании анализа содержимого фрагмента, почему выбраны эти схемы.]
   **Схемы:** [Перечислить , через запятую]
   **Фрагмент:** "[Оригинальный текст фрагмента]"

2. **Рассуждение:** ...
   **Схемы:** ...
   **Фрагмент:** "..."

(При необходимости используйте markdown для визуального отделения 
фрагментов.)

# Пример (иллюстративный, не используйте описание схем; 
используйте реальные смысловые фрагменты):

**Пример 1 (фрагмент разъясняющей статьи):**

1. **Рассуждение:** Здесь приведено определение термина "Boldsea". 
Текст чётко описывает его суть и ключевые характеристики, 
подходит под схему "Definition".
   **Схемы:** Definition
   **Фрагмент:** "Boldsea — это «семантический компьютер»: 
   все данные фиксируются как неизменяемый поток событий 
   (Event Sourcing)..."



(В полной разметке каждый реальный фрагмент должен быть оформлен 
аналогично и глубже — если в тексте есть таблица или несколько 
взаимосвязанных блоков, выделяйте их как отдельные фрагменты.)

# Особые случаи и уточнения

- Если фрагмент попадает сразу под несколько схем — приводите их 
все, обосновывая каждую.
- Не изменяйте оригинальный текст фрагмента.
- Не разделяйте смысловые блоки чрезмерно мелко (концентрируйтесь 
на логических завершённых единицах).

# Output Format

Строго структурированный, пронумерованный список фрагментов. 
Для каждого:
- короткое рассуждение (причина выбора схемы),
- название схем(ы) ,
- сам фрагмент (в оригинале).

Не группируйте фрагменты и не вставляйте промежуточных заголовков 
или комментариев. Форматируйте для удобства дальнейшего 
программного парсинга (строго по шаблону выше).



# Notes

- Всегда начинайте с рассуждения до вывода схемы.
- Для сложных фрагментов не забывайте обосновывать выбор каждой из 
схем.
- Ваша цель — сделать структуру, в которой автоматизированная 
система Boldsea сможет однозначно распознать и материализовать 
выделенные фрагменты согласно присвоенным схемам.

**Напоминание:** 
Для каждого фрагмента: сначала обосновать выбор схемы (рассуждение, явно!), затем назвать одну или несколько схем (по-русски), затем сам фрагмент (не изменяя текст).
Ответ — это полный исходный текст, разбитый на осмысленные 
фрагменты по указанной системе.

Если исходный текст очень длинный, используйте столько фрагментов, 
сколько требует структура и смысл, не объединяйте разнородное, 
не дробите сверх меры.





"""
    


# Инструкция для шага 2 (требование строгого JSON от gpt-4.1):
prompt_json_doc = """

Задача. Из входного текста, содержащего пронумерованные блоки, для каждого блока извлечь:
	1.	номер фрагмента; 2) значение поля «Схемы»; 3) сам текст после «Фрагмент:».

Выход. Один JSON-объект вида { "fragments": [...] }, где каждый элемент — отдельный фрагмент.

Ключи (англ.):
	•	fragment_id — номер фрагмента (integer).
	•	schema — схема/типы из строки «Схемы: …».
Если значений несколько, разбить по запятой/точке с запятой → массив строк; если одно — можно оставить строкой или массивом из одного элемента (предпочтительно массив).
	•	text — содержимое после «Фрагмент:», без внешних кавычек, с сохранением исходной пунктуации.

Правила извлечения:
	•	Номер берётся из начала блока вида ^\d+\. (например, 21. → 21).
	•	«Схемы: …» читать как список значений, trim пробелы, убрать служебные слова.
	•	«Фрагмент: …» — взять содержимое, удалить только внешние кавычки " при их наличии.
	•	Порядок элементов в fragments — как в исходном тексте (или по возрастанию fragment_id).
	•	Если в блоке нет «Фрагмент:», такой блок пропустить. Если нет «Схемы:», записать schema: [].
 
Пример результата для вашего текста:
{
  "fragments": [
    {
      "fragment_id": 21,
      "schema": ["Example"],
      "text": "извлеченный текст "
    },
    {
      "fragment_id": 22,
      "schema": ["Definition"],
      "text": "извлеченный текст "
    }
  ]
}



"""