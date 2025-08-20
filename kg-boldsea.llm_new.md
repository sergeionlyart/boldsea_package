# KG boldsea. словарь

## Примечание. после строки создания индивдов концептов добавляется служное отношение `SetModel` указывающее по какой модели будут создаваться предметные события, в граф оно не записывается. 

Concept: Instance: Author
Concept: Instance: Document
Concept: Instance: Fragment
Concept: Instance: Classifier
Concept: Instance: Category
Concept: Instance: Term
Concept: Instance: Schema Instruction


# Словарь для индексирования документации boldsea

# Инициация атрибутов
Attribute: Individual: name
: DataType: Text

Attribute: Individual: title
: DataType: Text

Attribute: Individual: text
: DataType: Text

Attribute: Individual: text_id
: DataType: Text

Attribute: Individual: fragment_anchor
: DataType: Text

Attribute: Individual: confidence
: DataType: Numeric

Attribute: Individual: definition
: DataType: Text

Attribute: Individual: description
: DataType: Text

Attribute: Individual: synonym
: DataType: Text
: Multiple: 1

Attribute: Individual: importance
: DataType: EnumType
: AttributeValue: High
: AttributeValue: Medium
: AttributeValue: Low

Attribute: Individual: mechanism
: DataType: Text

Attribute: Individual: prerequisites
: DataType: Text
: Multiple: 1

Attribute: Individual: constraints
: DataType: Text
: Multiple: 1

Attribute: Individual: type
: DataType: EnumType

Attribute: Individual: label
: DataType: Text

# Инициация отношений
Relation: Individual: author
: Domain: Document
: Range: Author
: Multiple: 1

Relation: Individual: document
: Domain: Fragment
: Range: Document

Relation: Individual: schema
: Domain: Fragment
: Range: Model

Relation: Individual: category
: Domain: Fragment
: Range: Category
: Multiple: 1

Relation: Individual: term
: Domain: Fragment
: Range: Term
: Multiple: 1

Relation: Individual: whole
: Domain: Fragment
: Range: Fragment

Relation: Individual: previous
: Domain: Fragment
: Range: Fragment

Relation: Individual: references
: Domain: Fragment
: Range: Fragment
: Multiple: 1

Relation: Individual: includes
: Domain: Schema
: Range: Term
: Multiple: 1

Relation: Individual: target
: Domain: Schema
: Range: Term

Relation: Individual: comparator
: Domain: Schema
: Range: Term

Relation: Individual: criterion
: Domain: Schema
: Range: Term
: Multiple: 1

Relation: Individual: advantage
: Domain: Schema
: Range: Term

Relation: Individual: cause
: Domain: Schema
: Range: Term
: Multiple: 1

Relation: Individual: effect
: Domain: Schema
: Range: Term
: Multiple: 1

Relation: Individual: domain
: Range: Term
: Multiple: 1

Relation: Individual: illustrates
: Domain: Schema
: Range: Term
: Multiple: 1

Relation: Individual: broader
: Domain: Term
: Range: Term

Relation: Individual: related
: Domain: Term
: Range: Term
: Multiple: 1

Relation: Individual: classifier
: Domain: Category
: Range: Classifier

# Дополнительные отношения для семантических схем
Relation: Individual: system_terms
: Range: Term
: Multiple: 1

Relation: Individual: purpose_terms
: Range: Term
: Multiple: 1

Relation: Individual: interfaces_terms
: Range: Term
: Multiple: 1

Relation: Individual: pattern_terms
: Range: Term
: Multiple: 1

Relation: Individual: input_types
: Range: Term
: Multiple: 1

Relation: Individual: output_types
: Range: Term
: Multiple: 1

Relation: Individual: process_category
: Range: Term

Relation: Individual: involves_components
: Range: Term
: Multiple: 1

Relation: Individual: demonstrates
: Range: Term
: Multiple: 1

Relation: Individual: problem_domain
: Range: Term
: Multiple: 1

Relation: Individual: solution_components
: Range: Term
: Multiple: 1

Relation: Individual: actors
: Range: Term
: Multiple: 1

Relation: Individual: concept_ref
: Range: Term

Relation: Individual: technologies
: Range: Term
: Multiple: 1

Relation: Individual: key_features
: Range: Term
: Multiple: 1

Relation: Individual: language
: Range: Term

Relation: Individual: keywords
: Range: Term
: Multiple: 1

Relation: Individual: items
: Range: Term
: Multiple: 1

Relation: Individual: rows
: Range: Term
: Multiple: 1

Relation: Individual: columns
: Range: Term
: Multiple: 1

Relation: Individual: values
: Range: Term
: Multiple: 1

Relation: Individual: advantages
: Range: Term
: Multiple: 1

Relation: Individual: disadvantages
: Range: Term
: Multiple: 1

Relation: Individual: example_fragments
: Range: Fragment

Relation: Individual: alternative_solutions
: Range: Term
: Multiple: 1

# Атрибуты для SchemaInstruction
Attribute: Individual: display_name
: DataType: Text

Attribute: Individual: model_identifier
: DataType: Text

Attribute: Individual: llm_prompt_template
: DataType: Text

Attribute: Individual: extraction_fields
: DataType: Text


# Объявление словаря
Vocabulary: Individual: Boldsea Indexing Vocabulary
: SetModel: Model_Vocabulary 
: Attributes: name
: Attributes: title
: Attributes: text
: Attributes: text_id
: Attributes: fragment_anchor
: Attributes: confidence
: Attributes: definition
: Attributes: description
: Attributes: synonym
: Attributes: importance
: Attributes: mechanism
: Attributes: prerequisites
: Attributes: constraints
: Attributes: type
: Attributes: label
: Relations: author
: Relations: document
: Relations: schema
: Relations: category
: Relations: term
: Relations: whole
: Relations: previous
: Relations: references
: Relations: includes
: Relations: target
: Relations: comparator
: Relations: criterion
: Relations: advantage
: Relations: cause
: Relations: effect
: Relations: domain
: Relations: illustrates
: Relations: broader
: Relations: related
: Relations: classifier
: Relations: system_terms
: Relations: purpose_terms
: Relations: interfaces_terms
: Relations: pattern_terms
: Relations: input_types
: Relations: output_types
: Relations: process_category
: Relations: involves_components
: Relations: demonstrates
: Relations: problem_domain
: Relations: solution_components
: Relations: actors
: Relations: concept_ref
: Relations: technologies
: Relations: key_features
: Relations: language
: Relations: keywords
: Relations: items
: Relations: rows
: Relations: columns
: Relations: values
: Relations: advantages
: Relations: disadvantages
: Attributes: display_name
: Attributes: model_identifier
: Attributes: llm_prompt_template
: Attributes: extraction_fields
: Relations: example_fragments
: Relations: alternative_solutions

# Модель документа
Document: Model: Model Document
: Attribute: title
:: Required: 1
: Relation: author         
:: Multiple: 1

# Модель автора
Author: Model: Model Author  
: Attribute: name
:: Required: 1

# Семантические схемы

## Модель инструкции

Schema Instruction: Model: Model Schema Instruction
: Attribute: display_name
:: Required: 1
:: DataType: String
: Attribute: description
:: Required: 1 
:: DataType: Text
: Attribute: model_identifier
:: Required: 1
:: DataType: String
:: UniqueIdentifier: 1
: Attribute: llm_prompt_template
:: Required: 1
:: DataType: Text
: Attribute: extraction_fields # JSON-описание полей для извлечения
:: DataType: Text
: Relation: example_fragments
:: Multiple: 1

# Индивиды инструкции

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
: extraction_fields: '{"target": "Range: Term", "advantages": "Range: Term, Multiple: 1", "disadvantages": "Range: Term, Multiple: 1", "keywords": "Range: Term, Multiple: 1"}'

## 3. Модели схем

### Базовые универсальные схемы

# Фрагмент по схеме "Определение"
Fragment: Model: Definition
: Relation: term # Определяемый термин
:: Range: Term
: Relation: includes # Термины, содержащиеся в определении
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Сравнение"
Fragment: Model: Comparison
: Relation: target # Основной объект сравнения
:: Range: Term
: Relation: comparator # То, с чем сравнивается
:: Range: Term
: Relation: criterion # Критерии сравнения
:: Range: Term
:: Multiple: 1
: Relation: advantage # У кого преимущество по критерию
:: SetRange: [$.target, $.comparator]
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Причинно-следственная связь"
Fragment: Model: Causal Relation
: Relation: cause # Причины, факторы влияния
:: Range: Term
:: Multiple: 1
: Relation: effect # Следствия, результаты
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Контекст применения"
Fragment: Model: Application Context
: Relation: domain # Области применения
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Пример"
Fragment: Model: Example
: Relation: illustrates # Что иллюстрирует пример
:: Range: Term
:: Multiple: 1
: Attribute: type # Тип примера
:: DataType: EnumType
:: AttributeValue: "code"
:: AttributeValue: "scenario"
:: AttributeValue: "analogy"
:: AttributeValue: "counter-example"
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

### Архитектурно-технические схемы

# Фрагмент по схеме "Архитектурный компонент"
Fragment: Model: Architectural Component
: Relation: system_terms # К какой системе относится
:: Range: Term
:: Multiple: 1
: Relation: purpose_terms # Назначение компонента
:: Range: Term
:: Multiple: 1
: Relation: interfaces_terms # С чем взаимодействует
:: Range: Term
:: Multiple: 1
: Relation: pattern_terms # Используемые архитектурные паттерны
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Технический процесс"
Fragment: Model: Technical Process
: Relation: input_types # Типы входных данных
:: Range: Term
:: Multiple: 1
: Relation: output_types # Типы выходных данных
:: Range: Term
:: Multiple: 1
: Relation: process_category # Категория процесса
:: Range: Term
: Relation: involves_components # Задействованные компоненты
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Алгоритм/Метод"
Fragment: Model: Algorithm
: Relation: input_types # Типы входных данных
:: Range: Term
:: Multiple: 1
: Relation: output_types # Результаты выполнения
:: Range: Term
:: Multiple: 1
: Relation: involves_components # Используемые концепты
:: Range: Term
:: Multiple: 1
: Relation: process_category # Тип алгоритма
:: Range: Term
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

### Концептуальные схемы

# Фрагмент по схеме "Концептуальная модель"
Fragment: Model: Conceptual Model
: Relation: target # Центральный концепт модели
:: Range: Term
: Relation: involves_components # Связанные концепты
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Принцип/Подход"
Fragment: Model: Principle
: Relation: target # Принцип или подход
:: Range: Term
: Relation: domain # К чему применяется
:: Range: Term
:: Multiple: 1
: Relation: comparator # С чем контрастирует
:: Range: Term
:: Multiple: 1
: Relation: demonstrates # Что обеспечивает
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

### Проблемно-ориентированные схемы

# Фрагмент по схеме "Проблема и решение"
Fragment: Model: Problem Solution
: Relation: problem_domain # Область проблемы
:: Range: Term
:: Multiple: 1
: Relation: solution_components # Основные компоненты решения
:: Range: Term
:: Multiple: 1
: Relation: alternative_solutions # Альтернативные решения
:: Range: Term
:: Multiple: 1
: Relation: keywords # Ключевые термины
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Ограничения и вызовы"
Fragment: Model: Limitations And Challenges
: Relation: target # К чему относится ограничение
:: Range: Term
: Relation: problem_domain # Типы ограничений/проблем
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

### Функциональные схемы

# Фрагмент по схеме "Функциональность"
Fragment: Model: Functionality
: Relation: system_terms # Система/компонент
:: Range: Term
: Relation: purpose_terms # Функции
:: Range: Term
:: Multiple: 1
: Relation: involves_components # Зависимости
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Возможности"
Fragment: Model: Capabilities
: Relation: target # Что обладает возможностями
:: Range: Term
: Relation: purpose_terms # Типы возможностей
:: Range: Term
:: Multiple: 1
: Relation: demonstrates # Обеспечиваемые сценарии
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $$.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

### Интеграционные схемы

# Фрагмент по схеме "Интеграция систем"
Fragment: Model: System Integration
: Relation: target # Основная система
:: Range: Term
: Relation: comparator # Интегрируемая система
:: Range: Term
: Relation: interfaces_terms # Точки интеграции
:: Range: Term
:: Multiple: 1
: Relation: process_category # Метод интеграции
:: Range: Term
: Attribute: text 
: Attribute: text_id
:: Condition: $.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Взаимодействие компонентов"
Fragment: Model: Component Interaction
: Relation: target # Инициатор взаимодействия
:: Range: Term
: Relation: comparator # Цель взаимодействия
:: Range: Term
: Relation: process_category # Тип взаимодействия
:: Range: Term
: Relation: involves_components # Посредники
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

### Прикладные схемы

# Фрагмент по схеме "Сценарий использования"
Fragment: Model: Use Case
: Relation: domain # Предметная область
:: Range: Term
: Relation: actors # Участники сценария
:: Range: Term
:: Multiple: 1
: Relation: demonstrates # Что демонстрирует
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Реализация концепции"
Fragment: Model: Concept Implementation
: Relation: concept_ref # Реализуемый концепт
:: Range: Term
: Relation: technologies # Используемые технологии
:: Range: Term
:: Multiple: 1
: Relation: key_features # Ключевые особенности
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

### Дополнительные схемы для полного покрытия

# Фрагмент по схеме "Фрагмент кода"
Fragment: Model: Code Snippet
: Relation: language # Язык программирования или формат
:: Range: Term
: Relation: illustrates # Что демонстрирует код
:: Range: Term
:: Multiple: 1
: Relation: input_types # Входные параметры
:: Range: Term
:: Multiple: 1
: Relation: output_types # Выходные значения
:: Range: Term
:: Multiple: 1
: Relation: keywords # Ключевые термины
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Перечисление/Список"
Fragment: Model: Enumeration
: Relation: category # Тип или тема списка
:: Range: Term
: Relation: items # Элементы списка
:: Range: Term
:: Multiple: 1
: Relation: keywords # Ключевые термины
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Таблица/Матрица"
Fragment: Model: Table Analysis
: Relation: rows # Строки таблицы
:: Range: Term
:: Multiple: 1
: Relation: columns # Столбцы таблицы
:: Range: Term
:: Multiple: 1
: Relation: values # Значения в ячейках
:: Range: Term
:: Multiple: 1
: Relation: keywords # Ключевые термины
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Фрагмент по схеме "Преимущества и недостатки"
Fragment: Model: Advantage Disadvantage
: Relation: target # Объект анализа
:: Range: Term
: Relation: advantages # Преимущества
:: Range: Term
:: Multiple: 1
: Relation: disadvantages # Недостатки
:: Range: Term
:: Multiple: 1
: Relation: keywords # Ключевые термины
:: Range: Term
:: Multiple: 1
: Attribute: text 
: Attribute: text_id
:: Condition: $.text == undefined  # либо text, либо text_id
: Relation: document
:: Required: 1
:: Immutable: 1
: Attribute: fragment_anchor
: Relation: category
:: Multiple: 1
: Relation: term
:: Multiple: 1  
: Relation: whole
:: Range: Fragment
: Relation: previous
:: Range: Fragment
: Relation: references
:: Multiple: 1
:: Range: Fragment
: Attribute: confidence
:: ValueCondition: $.confidence >= 0 && $.confidence <= 1

# Классификатор

# Модели 
Classifier: Model: Model Classifier
: Attribute: definition

Category: Model: Model Category
: Relation: classifier
:: Multiple: 1
: Attribute: description

# Классификаторы и категории

# Component
Classifier: Individual: Component
: SetModel: Model Classifier
: definition: Классификация по технологическим компонентам системы boldsea

Category: Individual: Engine
: SetModel: Model Category
: classifier: Component
: description: Семантический движок и его компоненты

Category: Individual: Network
: SetModel: Model Category
: classifier: Component
: description: P2P сеть, консенсус, распределенность

Category: Individual: UI
: SetModel: Model Category
: classifier: Component
: description: Интерфейсы и пользовательский опыт

Category: Individual: Storage
: SetModel: Model Category
: classifier: Component
: description: Хранилища данных, граф знаний

Category: Individual: Security
: SetModel: Model Category
: classifier: Component
: description: Безопасность и криптография

Category: Individual: Integration
: SetModel: Model Category
: classifier: Component
: description: Интеграция с внешними системами

Category: Individual: AI
: SetModel: Model Category
: classifier: Component
: description: Интеграция с LLM и AI

Category: Individual: Workflow
: SetModel: Model Category
: classifier: Component
: description: Моделирование бизнес-процессов

Category: Individual: Semantics
: SetModel: Model Category
: classifier: Component
: description: Семантические технологии

Category: Individual: API
: SetModel: Model Category
: classifier: Component
: description: API и программные интерфейсы

# Solution
Classifier: Individual: Solution
: SetModel: Model Classifier
: definition: Классификация по типам решаемых задач

Category: Individual: Business Process
: SetModel: Model Category
: classifier: Solution
: description: Бизнес-процессы

Category: Individual: Document Management
: SetModel: Model Category
: classifier: Solution
: description: Документооборот

Category: Individual: Knowledge Management
: SetModel: Model Category
: classifier: Solution
: description: Управление знаниями

Category: Individual: Data Integration
: SetModel: Model Category
: classifier: Solution
: description: Интеграция данных

Category: Individual: Automation
: SetModel: Model Category
: classifier: Solution
: description: Автоматизация

Category: Individual: Compliance
: SetModel: Model Category
: classifier: Solution
: description: Соответствие требованиям

Category: Individual: Scalability
: SetModel: Model Category
: classifier: Solution
: description: Масштабируемость

Category: Individual: Flexibility
: SetModel: Model Category
: classifier: Solution
: description: Гибкость систем

# Audience
Classifier: Individual: Audience
: SetModel: Model Classifier
: definition: Классификация по целевой аудитории

Category: Individual: Business Executives
: SetModel: Model Category
: classifier: Audience
: description: Руководители, принимающие решения

Category: Individual: Investors
: SetModel: Model Category
: classifier: Audience
: description: Инвесторы, венчурные фонды

Category: Individual: Business Analysts
: SetModel: Model Category
: classifier: Audience
: description: Бизнес-аналитики, функциональные консультанты

Category: Individual: Technical Analysts
: SetModel: Model Category
: classifier: Audience
: description: Системные аналитики, архитекторы

Category: Individual: Developers
: SetModel: Model Category
: classifier: Audience
: description: Разработчики, программисты

Category: Individual: Researchers
: SetModel: Model Category
: classifier: Audience
: description: Исследователи, академические круги

Category: Individual: End Users
: SetModel: Model Category
: classifier: Audience
: description: Конечные пользователи системы

Category: Individual: Integrators
: SetModel: Model Category
: classifier: Audience
: description: Системные интеграторы, консультанты по внедрению

# Level
Classifier: Individual: Level
: SetModel: Model Classifier
: definition: Классификация по уровню представления информации

Category: Individual: General
: SetModel: Model Category
: classifier: Level
: description: Общие разъяснения доступные всем

Category: Individual: Domain Specific
: SetModel: Model Category
: classifier: Level
: description: Предметно-ориентированные объяснения

Category: Individual: Technical
: SetModel: Model Category
: classifier: Level
: description: Технические детали для специалистов

Category: Individual: Implementation
: SetModel: Model Category
: classifier: Level
: description: Детали реализации и внедрения

Category: Individual: Theoretical
: SetModel: Model Category
: classifier: Level
: description: Теоретические основы и концепции

Category: Individual: Philosophical Foundation
: SetModel: Model Category
: classifier: Level
: description: Философские основы

# Difficulty
Classifier: Individual: Difficulty
: SetModel: Model Classifier
: definition: Классификация по уровню сложности материала

Category: Individual: Basic
: SetModel: Model Category
: classifier: Difficulty
: description: Основные понятия, простые определения

Category: Individual: Intermediate
: SetModel: Model Category
: classifier: Difficulty
: description: Детальные объяснения, примеры применения

Category: Individual: Advanced
: SetModel: Model Category
: classifier: Difficulty
: description: Глубокие технические детали, архитектурные решения

Category: Individual: Expert
: SetModel: Model Category
: classifier: Difficulty
: description: Специализированные знания, внутренние механизмы

# Detailing
Classifier: Individual: Detailing
: SetModel: Model Classifier
: definition: Классификация по степени детализации

Category: Individual: Overview
: SetModel: Model Category
: classifier: Detailing
: description: Общий обзор

Category: Individual: Summary
: SetModel: Model Category
: classifier: Detailing
: description: Краткое изложение

Category: Individual: Detailed
: SetModel: Model Category
: classifier: Detailing
: description: Подробное описание

Category: Individual: Comprehensive
: SetModel: Model Category
: classifier: Detailing
: description: Исчерпывающее изложение

Category: Individual: Implementation Guide
: SetModel: Model Category
: classifier: Detailing
: description: Руководство по реализации

Category: Individual: Formal Specification
: SetModel: Model Category
: classifier: Detailing
: description: Формальная спецификация

Category: Individual: Deep Dive
: SetModel: Model Category
: classifier: Detailing
: description: Глубокий анализ

# Functional purpose
Classifier: Individual: Functional purpose
: SetModel: Model Classifier
: definition: Классификация по функциональному назначению

Category: Individual: Conceptual
: SetModel: Model Category
: classifier: Functional purpose
: description: Концептуальные основы технологии

Category: Individual: Architectural
: SetModel: Model Category
: classifier: Functional purpose
: description: Архитектурные решения

Category: Individual: Operational
: SetModel: Model Category
: classifier: Functional purpose
: description: Операционные аспекты

Category: Individual: Strategic
: SetModel: Model Category
: classifier: Functional purpose
: description: Стратегические вопросы

Category: Individual: Commercial
: SetModel: Model Category
: classifier: Functional purpose
: description: Коммерческие аспекты

Category: Individual: Legal
: SetModel: Model Category
: classifier: Functional purpose
: description: Правовые и патентные вопросы

Category: Individual: Educational
: SetModel: Model Category
: classifier: Functional purpose
: description: Обучающие материалы

Category: Individual: Promotional
: SetModel: Model Category
: classifier: Functional purpose
: description: Промо-материалы и презентации

# Industry
Classifier: Individual: Industry
: SetModel: Model Classifier
: definition: Классификация по отраслям применения

Category: Individual: Universal
: SetModel: Model Category
: classifier: Industry
: description: Универсальные решения

Category: Individual: Finance
: SetModel: Model Category
: classifier: Industry
: description: Финансовые услуги

Category: Individual: Healthcare
: SetModel: Model Category
: classifier: Industry
: description: Здравоохранение

Category: Individual: Legal
: SetModel: Model Category
: classifier: Industry
: description: Юридические услуги

Category: Individual: Manufacturing
: SetModel: Model Category
: classifier: Industry
: description: Производство

Category: Individual: Government
: SetModel: Model Category
: classifier: Industry
: description: Государственный сектор

Category: Individual: Research
: SetModel: Model Category
: classifier: Industry
: description: Исследования и разработки

Category: Individual: Education
: SetModel: Model Category
: classifier: Industry
: description: Образование

Category: Individual: Retail
: SetModel: Model Category
: classifier: Industry
: description: Розничная торговля

# Data
Classifier: Individual: Data
: SetModel: Model Classifier
: definition: Классификация по типам данных

Category: Individual: Structured Data
: SetModel: Model Category
: classifier: Data
: description: Структурированные данные

Category: Individual: Unstructured Data
: SetModel: Model Category
: classifier: Data
: description: Неструктурированные данные

Category: Individual: Metadata
: SetModel: Model Category
: classifier: Data
: description: Метаданные

Category: Individual: Temporal Data
: SetModel: Model Category
: classifier: Data
: description: Темпоральные данные

Category: Individual: Semantic Data
: SetModel: Model Category
: classifier: Data
: description: Семантические данные

Category: Individual: Business Rules
: SetModel: Model Category
: classifier: Data
: description: Бизнес-правила

# Architecture
Classifier: Individual: Architecture
: SetModel: Model Classifier
: definition: Классификация по архитектурным подходам

Category: Individual: Event Driven
: SetModel: Model Category
: classifier: Architecture
: description: Событийно-ориентированные аспекты

Category: Individual: Semantic Modeling
: SetModel: Model Category
: classifier: Architecture
: description: Семантическое моделирование

Category: Individual: Dataflow
: SetModel: Model Category
: classifier: Architecture
: description: Dataflow-архитектура

Category: Individual: No Code
: SetModel: Model Category
: classifier: Architecture
: description: No-code подходы

Category: Individual: Blockchain
: SetModel: Model Category
: classifier: Architecture
: description: Блокчейн и распределенные технологии

Category: Individual: AI-интеграция
: SetModel: Model Category
: classifier: Architecture
: description: Интеграция с искусственным интеллектом

Category: Individual: Workflow Management
: SetModel: Model Category
: classifier: Architecture
: description: Управление workflow

# Application
Classifier: Individual: Application
: SetModel: Model Classifier
: definition: Классификация по масштабу применения

Category: Individual: Personal
: SetModel: Model Category
: classifier: Application
: description: Персональное использование

Category: Individual: Team
: SetModel: Model Category
: classifier: Application
: description: Командная работа

Category: Individual: Departmental
: SetModel: Model Category
: classifier: Application
: description: Уровень подразделения

Category: Individual: Enterprise
: SetModel: Model Category
: classifier: Application
: description: Корпоративный уровень

Category: Individual: Inter Organizational
: SetModel: Model Category
: classifier: Application
: description: Межорганизационное взаимодействие

Category: Individual: Ecosystem
: SetModel: Model Category
: classifier: Application
: description: Экосистемный уровень

Category: Individual: Global
: SetModel: Model Category
: classifier: Application
: description: Глобальное применение

# Actor
Classifier: Individual: Actor
: SetModel: Model Classifier
: definition: Классификация по типам акторов

Category: Individual: Passive Observer
: SetModel: Model Category
: classifier: Actor
: description: Пассивный наблюдатель

Category: Individual: Active Reader
: SetModel: Model Category
: classifier: Actor
: description: Активный читатель

Category: Individual: Interactive User
: SetModel: Model Category
: classifier: Actor
: description: Интерактивный пользователь

Category: Individual: Content Creator
: SetModel: Model Category
: classifier: Actor
: description: Создатель контента

Category: Individual: Process Participant
: SetModel: Model Category
: classifier: Actor
: description: Участник процесса

Category: Individual: System Administrator
: SetModel: Model Category
: classifier: Actor
: description: Системный администратор

Category: Individual: Network Validator
: SetModel: Model Category
: classifier: Actor
: description: Валидатор сети

Category: Individual: Ecosystem Governor
: SetModel: Model Category
: classifier: Actor
: description: Управляющий экосистемой

# Stage
Classifier: Individual: Stage
: SetModel: Model Classifier
: definition: Классификация по стадии развития

Category: Individual: Concept
: SetModel: Model Category
: classifier: Stage
: description: Концептуальная стадия

Category: Individual: Proof of Concept
: SetModel: Model Category
: classifier: Stage
: description: Proof of concept

Category: Individual: Prototype
: SetModel: Model Category
: classifier: Stage
: description: Прототип

Category: Individual: MVP
: SetModel: Model Category
: classifier: Stage
: description: Минимальный жизнеспособный продукт

Category: Individual: Alpha
: SetModel: Model Category
: classifier: Stage
: description: Альфа-версия

Category: Individual: Beta
: SetModel: Model Category
: classifier: Stage
: description: Бета-версия

Category: Individual: Production Ready
: SetModel: Model Category
: classifier: Stage
: description: Готово к производству

Category: Individual: Market Ready
: SetModel: Model Category
: classifier: Stage
: description: Готово к рынку

# Temporary
Classifier: Individual: Temporary
: SetModel: Model Classifier
: definition: Классификация по временной перспективе

Category: Individual: Past
: SetModel: Model Category
: classifier: Temporary
: description: Историческая ретроспектива

Category: Individual: Present
: SetModel: Model Category
: classifier: Temporary
: description: Текущее состояние

Category: Individual: Near Future
: SetModel: Model Category
: classifier: Temporary
: description: Ближайшие планы

Category: Individual: Long Term
: SetModel: Model Category
: classifier: Temporary
: description: Долгосрочная перспектива

# Innovativeness
Classifier: Individual: Innovativeness
: SetModel: Model Classifier
: definition: Классификация по степени инновационности

Category: Individual: Conventional Practice
: SetModel: Model Category
: classifier: Innovativeness
: description: Общепринятые практики

Category: Individual: Best Practice
: SetModel: Model Category
: classifier: Innovativeness
: description: Лучшие практики

Category: Individual: Innovative Approach
: SetModel: Model Category
: classifier: Innovativeness
: description: Инновационные подходы

Category: Individual: Experimental Concept
: SetModel: Model Category
: classifier: Innovativeness
: description: Экспериментальные концепции

Category: Individual: Disruptive Innovation
: SetModel: Model Category
: classifier: Innovativeness
: description: Разрушительные инновации

Category: Individual: Paradigm Shift
: SetModel: Model Category
: classifier: Innovativeness
: description: Смена парадигм

# Economic
Classifier: Individual: Economic
: SetModel: Model Classifier
: definition: Классификация по экономическим моделям

Category: Individual: Licensing
: SetModel: Model Category
: classifier: Economic
: description: Лицензирование

Category: Individual: SaaS
: SetModel: Model Category
: classifier: Economic
: description: SaaS модель

Category: Individual: On Premise
: SetModel: Model Category
: classifier: Economic
: description: On-premise решения

Category: Individual: Open Source
: SetModel: Model Category
: classifier: Economic
: description: Открытый исходный код

Category: Individual: Consulting
: SetModel: Model Category
: classifier: Economic
: description: Консультационные услуги

Category: Individual: Marketplace
: SetModel: Model Category
: classifier: Economic
: description: Модель маркетплейса

Category: Individual: Token Economy
: SetModel: Model Category
: classifier: Economic
: description: Токен-экономика

# Competition
Classifier: Individual: Competition
: SetModel: Model Classifier
: definition: Классификация по конкурентным аспектам

Category: Individual: Unique Advantages
: SetModel: Model Category
: classifier: Competition
: description: Уникальные преимущества

Category: Individual: Market Differentiation
: SetModel: Model Category
: classifier: Competition
: description: Дифференциация на рынке

Category: Individual: Competitor Analysis
: SetModel: Model Category
: classifier: Competition
: description: Анализ конкурентов

Category: Individual: Market Positioning
: SetModel: Model Category
: classifier: Competition
: description: Позиционирование

Category: Individual: Value Proposition
: SetModel: Model Category
: classifier: Competition
: description: Ценностное предложение

Category: Individual: Technology Comparison
: SetModel: Model Category
: classifier: Competition
: description: Сравнение технологий

# Information
Classifier: Individual: Information
: SetModel: Model Classifier
: definition: Классификация по типам информации

Category: Individual: Factual
: SetModel: Model Category
: classifier: Information
: description: Фактическая информация

Category: Individual: Analytical
: SetModel: Model Category
: classifier: Information
: description: Аналитические материалы

Category: Individual: Comparative
: SetModel: Model Category
: classifier: Information
: description: Сравнительные данные

Category: Individual: Predictive
: SetModel: Model Category
: classifier: Information
: description: Прогнозы и планы

Category: Individual: Historical
: SetModel: Model Category
: classifier: Information
: description: Историческая информация

Category: Individual: Statistical
: SetModel: Model Category
: classifier: Information
: description: Статистические данные

Category: Individual: Testimonial
: SetModel: Model Category
: classifier: Information
: description: Отзывы и мнения

Category: Individual: Case Study
: SetModel: Model Category
: classifier: Information
: description: Кейсы и примеры

# Content
Classifier: Individual: Content
: SetModel: Model Classifier
: definition: Классификация по формату контента

Category: Individual: Narrative
: SetModel: Model Category
: classifier: Content
: description: Повествовательный формат

Category: Individual: List
: SetModel: Model Category
: classifier: Content
: description: Списки и перечисления

Category: Individual: Table
: SetModel: Model Category
: classifier: Content
: description: Табличные данные

Category: Individual: Diagram
: SetModel: Model Category
: classifier: Content
: description: Диаграммы и схемы

Category: Individual: Code
: SetModel: Model Category
: classifier: Content
: description: Код и технические примеры

Category: Individual: Dialogue
: SetModel: Model Category
: classifier: Content
: description: Диалоги и Q&A

Category: Individual: Bullet Points
: SetModel: Model Category
: classifier: Content
: description: Тезисы и ключевые моменты

Category: Individual: Formal Specification
: SetModel: Model Category
: classifier: Content
: description: Формальные спецификации

Category: Individual: Mathematical Notation
: SetModel: Model Category
: classifier: Content
: description: Математическая нотация

# Abstractness
Classifier: Individual: Abstractness
: SetModel: Model Classifier
: definition: Классификация по уровню абстракции

Category: Individual: Philosophical
: SetModel: Model Category
: classifier: Abstractness
: description: Философский уровень

Category: Individual: Conceptual
: SetModel: Model Category
: classifier: Abstractness
: description: Концептуальный уровень

Category: Individual: Logical
: SetModel: Model Category
: classifier: Abstractness
: description: Логический уровень

Category: Individual: Physical
: SetModel: Model Category
: classifier: Abstractness
: description: Физический уровень

Category: Individual: Implementation
: SetModel: Model Category
: classifier: Abstractness
: description: Уровень реализации

# Impact
Classifier: Individual: Impact
: SetModel: Model Classifier
: definition: Классификация по типу воздействия

Category: Individual: Disruptive
: SetModel: Model Category
: classifier: Impact
: description: Разрушительное влияние

Category: Individual: Evolutionary
: SetModel: Model Category
: classifier: Impact
: description: Эволюционное развитие

Category: Individual: Complementary
: SetModel: Model Category
: classifier: Impact
: description: Дополняющие решения

Category: Individual: Replacement
: SetModel: Model Category
: classifier: Impact
: description: Замещение существующих решений

Category: Individual: Enabling
: SetModel: Model Category
: classifier: Impact
: description: Поддерживающие технологии

# Relevance
Classifier: Individual: Relevance
: SetModel: Model Classifier
: definition: Классификация по актуальности

Category: Individual: Current
: SetModel: Model Category
: classifier: Relevance
: description: Актуальная информация

Category: Individual: Legacy
: SetModel: Model Category
: classifier: Relevance
: description: Устаревшая информация

Category: Individual: Experimental
: SetModel: Model Category
: classifier: Relevance
: description: Экспериментальные разработки

# Source
Classifier: Individual: Source
: SetModel: Model Classifier
: definition: Классификация по источникам

Category: Individual: Official Documentation
: SetModel: Model Category
: classifier: Source
: description: Официальная документация

Category: Individual: Patent
: SetModel: Model Category
: classifier: Source
: description: Патентные материалы

Category: Individual: Research Paper
: SetModel: Model Category
: classifier: Source
: description: Научные статьи

Category: Individual: Implementation Guide
: SetModel: Model Category
: classifier: Source
: description: Руководства по реализации

# AI Integration (дополнение)
Classifier: Individual: AI Integration
: SetModel: Model Classifier
: definition: Классификация по аспектам интеграции ИИ

Category: Individual: LLM Usage
: SetModel: Model Category
: classifier: AI Integration
: description: Использование больших языковых моделей

Category: Individual: Machine Learning
: SetModel: Model Category
: classifier: AI Integration
: description: Машинное обучение

Category: Individual: Neural Networks
: SetModel: Model Category
: classifier: AI Integration
: description: Нейронные сети

# Scalability (дополнение)
Classifier: Individual: Scalability Type
: SetModel: Model Classifier
: definition: Классификация по аспектам масштабируемости

Category: Individual: Vertical
: SetModel: Model Category
: classifier: Scalability Type
: description: Вертикальное масштабирование

Category: Individual: Horizontal
: SetModel: Model Category
: classifier: Scalability Type
: description: Горизонтальное масштабирование

Category: Individual: Cloud
: SetModel: Model Category
: classifier: Scalability Type
: description: Облачное масштабирование

# Performance (дополнение)
Classifier: Individual: Performance
: SetModel: Model Classifier
: definition: Классификация по аспектам производительности

Category: Individual: High Throughput
: SetModel: Model Category
: classifier: Performance
: description: Высокая пропускная способность

Category: Individual: Low Latency
: SetModel: Model Category
: classifier: Performance
: description: Низкая задержка

Category: Individual: Real Time
: SetModel: Model Category
: classifier: Performance
: description: Реальное время

# Модель термина

Term: Model: Model Term
: Attribute: definition 
: Attribute: synonym
:: Multiple: 1
: Attribute: importance
: Relation: domain
:: Range: Term
:: Multiple: 1
: Relation: broader    # родовое понятие
:: Range: Term
: Relation: related    # ассоциативные связи
:: Range: Term
:: Multiple: 1

# Домены (термины верхнего уровня)

Term: Individual: архитектура
: SetModel: Model Term
: definition: Область знаний, связанная с архитектурными решениями и подходами в boldsea
: importance: High

Term: Individual: моделирование деятельности
: SetModel: Model Term
: definition: Область знаний, связанная с построением моделей бизнес-процессов и организационной деятельности
: importance: High

Term: Individual: ограничивающие свойства
: SetModel: Model Term
: definition: Область знаний о свойствах, накладывающих ограничения на создание и значения событий
: importance: High

Term: Individual: сеть
: SetModel: Model Term
: definition: Область знаний о сетевой архитектуре и распределенных аспектах boldsea
: importance: Medium

Term: Individual: бизнес
: SetModel: Model Term
: definition: Область знаний о бизнес-применении и позиционировании boldsea
: importance: Medium

Term: Individual: интерфейс
: SetModel: Model Term
: definition: Область знаний о пользовательских интерфейсах и взаимодействии с системой
: importance: Medium

Term: Individual: запросы
: SetModel: Model Term
: definition: Область знаний о языках запросов и выражений в boldsea
: importance: Medium

Term: Individual: сравнение
: SetModel: Model Term
: definition: Область знаний о сравнении boldsea с другими технологиями и подходами
: importance: Medium

Term: Individual: событийная семантика
: SetModel: Model Term
: definition: Область знаний о событийно-семантическом подходе к моделированию
: importance: High

Term: Individual: приложение
: SetModel: Model Term
: definition: Область знаний о приложениях и системах на основе boldsea
: importance: Medium

Term: Individual: ontology
: SetModel: Model Term
: definition: Область знаний об онтологиях и семантических технологиях
: importance: Medium

Term: Individual: ai-интеграция
: SetModel: Model Term
: definition: Область знаний об интеграции с искусственным интеллектом
: importance: High

# Базовые концепты данных

Term: Individual: data element
: SetModel: Model Term
: definition: Базовый элемент данных в системе
: importance: Medium

# Основные концепты boldsea

Term: Individual: knowledge graph
: SetModel: Model Term
: definition: Граф семантически связанных фактов для хранения и анализа знаний
: synonym: граф знаний
: importance: High

Term: Individual: boldsea
: SetModel: Model Term
: definition: Подход к компьютерному моделированию деятельности, основанный на фиксации потока событий и создании исполняемых семантических моделей с использованием dataflow-идеологии
: synonym: boldsea-технология
: synonym: boldsea-архитектура
: synonym: событийно-семантический подход
: importance: High
: related: knowledge graph

Term: Individual: событие
: SetModel: Model Term
: definition: Фиксация актором наличия, изменения или создания объектов и значений их свойств в определенный момент времени
: synonym: event
: importance: High
: domain: boldsea
: broader: data element

Term: Individual: модельное событие
: SetModel: Model Term
: definition: Событие, фиксирующее наличие у концепта или действия некоторого свойства или акта; включает ограничения на значения свойств и условия актуализации
: synonym: model event
: synonym: шаблон события
: importance: High
: domain: boldsea
: broader: событие

Term: Individual: предметное событие
: SetModel: Model Term
: definition: Событие, фиксирующее конкретное значение свойства индивида концепта или конкретный акт действия; создается по модельному событию с учетом всех ограничений и условий
: synonym: reification event
: synonym: конкретное событие
: importance: High
: domain: boldsea
: broader: событие

Term: Individual: генезисное событие
: SetModel: Model Term
: definition: События, определяющие семантические примитивы, свойства, словари и ограничения
: synonym: genesis event
: synonym: базовое событие
: importance: Medium
: domain: boldsea

Term: Individual: актор
: SetModel: Model Term
: definition: Субъект, который различает, изменяет, действует; может быть ассоциирован с человеком, роботом, программным агентом, датчиком
: synonym: actor
: synonym: субъект
: synonym: агент
: importance: High
: domain: boldsea

Term: Individual: роль
: SetModel: Model Term
: definition: Отношение актора к проекту, фиксирующее права доступа актора к индивидам и их свойствам
: synonym: role
: synonym: права доступа
: importance: Medium
: domain: событийная семантика

Term: Individual: causals
: SetModel: Model Term
: definition: Поле формата события, фиксирующее отношение последовательности между событиями, задаваемые логическим выражением Condition
: synonym: причинные связи
: synonym: каузальные связи
: importance: Medium
: domain: boldsea

Term: Individual: концепт
: SetModel: Model Term
: definition: Семантический тип индивида, то, с чем актор ассоциирует индивид; различить индивид значит указать к какому концепту он относится
: synonym: concept
: synonym: понятие
: synonym: класс
: importance: High
: domain: событийная семантика

Term: Individual: индивид
: SetModel: Model Term
: definition: Уникальный объект, который различается, изменяется или создается актором; имеет пространственные и/или временные границы
: synonym: individual
: synonym: экземпляр
: synonym: объект
: importance: High
: domain: событийная семантика

Term: Individual: действие
: SetModel: Model Term
: definition: Семантический тип распределенного во времени индивида, представляющего собой частично упорядоченную последовательность событий
: synonym: action
: synonym: процесс
: synonym: активность
: importance: High
: domain: событийная семантика

Term: Individual: модель
: SetModel: Model Term
: definition: Упорядоченный список модельных событий, описывающих концепт или действие; индивиды концептов создаются по моделям
: synonym: model
: synonym: событийная модель
: importance: High
: domain: событийная семантика
: domain: моделирование деятельности

Term: Individual: ограничивающее свойство
: SetModel: Model Term
: definition: Свойство модельного события, накладывающее ограничения на возможность создания предметного события и на его значения
: synonym: restriction
: synonym: constraint
: synonym: ограничение
: importance: High
: domain: событийная семантика

Term: Individual: атрибут
: SetModel: Model Term
: definition: Свойство, которое актор различает у индивида непосредственно, безотносительно к другим индивидам
: synonym: attribute
: synonym: характеристика
: importance: Medium
: domain: событийная семантика

Term: Individual: отношение
: SetModel: Model Term
: definition: Свойство, которое актор фиксирует у индивида только относительно другого индивида
: synonym: relation
: synonym: связь
: importance: Medium
: domain: событийная семантика

Term: Individual: вложенное свойство
: SetModel: Model Term
: definition: Свойства, фиксируемые на корневых свойствах концепта (свойства свойств); допускается до 5 вложений
: synonym: nested property
: synonym: свойство свойства
: importance: Medium
: domain: событийная семантика

Term: Individual: темпоральность
: SetModel: Model Term
: definition: Свойство системы сохранять всю историю изменений данных с возможностью запросов к любому моменту времени
: synonym: temporality
: synonym: временность
: synonym: историчность
: importance: High
: domain: boldsea

# Архитектурные концепты

Term: Individual: dataflow-архитектура
: SetModel: Model Term
: definition: Архитектурный подход, при котором операции выполняются асинхронно по мере готовности данных, а не в строго заданном порядке
: synonym: dataflow
: synonym: dataflow-идеология
: synonym: архитектура потоков данных
: importance: High
: domain: архитектура

Term: Individual: control flow
: SetModel: Model Term
: definition: Традиционный подход к исполнению алгоритмов, при котором команды выполняются последовательно шаг за шагом
: synonym: архитектура фон Неймана
: synonym: последовательное выполнение
: importance: Medium
: domain: архитектура

Term: Individual: темпоральный граф
: SetModel: Model Term
: definition: Граф, отображающий временную последовательность событий и их взаимосвязи, имеет структуру направленного ациклического графа
: synonym: событийный граф
: synonym: DAG
: synonym: directed acyclic graph
: synonym: граф знаний
: importance: High
: domain: архитектура
: related: knowledge graph

Term: Individual: boldsea-движок
: SetModel: Model Term
: definition: Программный движок, который загружает семантические модели и исполняет их как алгоритм с генерацией предметных событий
: synonym: boldsea-engine
: synonym: семантический движок
: synonym: событийный движок
: synonym: workflow движок
: importance: High
: domain: архитектура

# Семантическое моделирование

Term: Individual: семантическое моделирование
: SetModel: Model Term
: definition: Подход к проектированию информационных систем, решающий задачу отделения смысловой составляющей от структуры приложения
: synonym: semantic modeling
: synonym: семантический подход
: importance: High
: domain: событийная семантика

# Ограничивающие свойства (конкретные)

Term: Individual: condition
: SetModel: Model Term
: definition: Условие, определяющее возможность совершения события; задается логическим выражением из значений предшествующих событий
: synonym: условие
: synonym: предусловие
: importance: High
: domain: ограничивающие свойства
: broader: ограничивающее свойство

Term: Individual: permission
: SetModel: Model Term
: definition: Ограничивающее свойство, определяющее права доступа акторов к созданию предметных событий по модельному событию
: synonym: права доступа
: synonym: разрешение
: importance: High
: domain: ограничивающие свойства
: broader: ограничивающее свойство
: related: роль

Term: Individual: SetValue
: SetModel: Model Term
: definition: Ограничивающее свойство, задающее автоматическое значение свойства через запрос или выражение
: synonym: автозаполнение
: synonym: вычисляемое значение
: importance: Medium
: domain: ограничивающие свойства
: broader: ограничивающее свойство

# Сетевые концепты

Term: Individual: кластер
: SetModel: Model Term
: definition: Группа узлов сети, работающих с одной группой семантических моделей в рамках предметной области
: synonym: cluster
: synonym: группа узлов
: synonym: сетевой кластер
: importance: Medium
: domain: сеть

Term: Individual: топик
: SetModel: Model Term
: definition: Тематический канал для обмена событиями между узлами сети по определенной модели или группе моделей
: synonym: topic
: synonym: канал
: synonym: тема
: importance: Medium
: domain: сеть

Term: Individual: консенсус
: SetModel: Model Term
: definition: Алгоритм согласования данных между узлами децентрализованной сети
: synonym: consensus
: synonym: согласование
: synonym: валидация
: importance: Medium
: domain: сеть

Term: Individual: p2p-сеть
: SetModel: Model Term
: definition: Одноранговая сеть, где узлы могут работать как клиенты и серверы одновременно
: synonym: peer-to-peer
: synonym: одноранговая сеть
: synonym: децентрализованная сеть
: importance: Medium
: domain: сеть

# Бизнес-концепты

Term: Individual: семантический компьютер
: SetModel: Model Term
: definition: Концептуальное позиционирование boldsea как системы, исполняющей семантические модели подобно тому, как обычный компьютер исполняет программы
: synonym: semantic computer
: synonym: семантический процессор
: importance: High
: domain: бизнес

Term: Individual: смарт-контракт
: SetModel: Model Term
: definition: В контексте boldsea - исполняемая семантическая модель действия, автоматически выполняющая бизнес-логику
: synonym: smart contract
: synonym: умный контракт
: synonym: цифровое соглашение
: importance: Medium
: domain: бизнес

Term: Individual: экосистема
: SetModel: Model Term
: definition: Сетевые кластеры с базовым набором приложений для реализации деятельности
: synonym: ecosystem
: synonym: сетевая экосистема
: importance: Medium
: domain: бизнес

# Приложения и системы

Term: Individual: словарь
: SetModel: Model Term
: definition: Список концептов или свойств, используемый для семантического описания предметной области
: synonym: vocabulary
: synonym: глоссарий
: synonym: справочник
: importance: Medium
: domain: приложение

Term: Individual: проект
: SetModel: Model Term
: definition: Концепт, совокупность индивидов концептов, действий и акторов, реализующих целенаправленную деятельность
: synonym: project
: synonym: организация
: synonym: экосистема
: importance: Medium
: domain: приложение

# Интерфейсы

Term: Individual: UI-контроллер
: SetModel: Model Term
: definition: Компонент системы, отвечающий за визуализацию и взаимодействие с пользователем
: synonym: UI controller
: synonym: контроллер интерфейса
: importance: Medium
: domain: интерфейс

Term: Individual: конструктор интерфейсов
: SetModel: Model Term
: definition: Инструмент для создания пользовательских интерфейсов без программирования на основе семантических моделей
: synonym: interface builder
: synonym: генератор UI
: importance: Medium
: domain: интерфейс

Term: Individual: no-code
: SetModel: Model Term
: definition: Подход к разработке приложений без традиционного программирования через визуальные интерфейсы
: synonym: визуальное программирование
: synonym: бескодовая разработка
: importance: Medium
: domain: интерфейс

Term: Individual: api
: SetModel: Model Term
: definition: Application Programming Interface для интеграции с внешними системами
: synonym: АПИ
: importance: Medium
: domain: интерфейс

# Запросы и выражения

Term: Individual: язык запросов
: SetModel: Model Term
: definition: Специальный язык для извлечения данных из темпорального графа событий
: synonym: query language
: synonym: ЯЗ
: importance: Medium
: domain: запросы

Term: Individual: язык выражений
: SetModel: Model Term
: definition: Язык для формулирования условий и ограничений в модельных событиях
: synonym: expression language
: synonym: язык условий
: importance: Medium
: domain: запросы

Term: Individual: query operator
: SetModel: Model Term
: definition: Операторы в языке запросов boldsea (EQ, NE, OR и т.д.)
: synonym: оператор запроса
: importance: Medium
: domain: запросы
: related: язык запросов

# Сравнение с другими технологиями

Term: Individual: BPMN
: SetModel: Model Term
: definition: Business Process Model and Notation - стандартизированная графическая нотация для моделирования бизнес-процессов
: synonym: БПМН
: synonym: нотация бизнес-процессов
: importance: Medium
: domain: сравнение

Term: Individual: task
: SetModel: Model Term
: definition: Элемент бизнес-процесса в BPMN, представляющий единичную работу
: synonym: задача
: importance: Medium
: domain: сравнение

Term: Individual: gateway
: SetModel: Model Term
: definition: Точка принятия решения в BPMN-процессе
: synonym: шлюз
: importance: Medium
: domain: сравнение
: related: task

Term: Individual: sequence flow
: SetModel: Model Term
: definition: Поток управления между элементами в BPMN
: synonym: последовательный поток
: importance: Medium
: domain: сравнение
: related: task

Term: Individual: RPA
: SetModel: Model Term
: definition: Robotic Process Automation - технология автоматизации бизнес-процессов с помощью программных роботов
: synonym: РПА
: synonym: роботизация процессов
: importance: Medium
: domain: сравнение

Term: Individual: workflow-движок
: SetModel: Model Term
: definition: Программная система для автоматизации бизнес-процессов согласно заранее определенным правилам
: synonym: workflow engine
: synonym: движок бизнес-процессов
: synonym: BPM-движок
: importance: Medium
: domain: сравнение

# Онтологии и семантические технологии

Term: Individual: ontology
: SetModel: Model Term
: definition: Формальная модель предметной области, описывающая концепты и отношения
: synonym: онтология
: importance: High

Term: Individual: RDF
: SetModel: Model Term
: definition: Resource Description Framework - модель представления данных семантического веба
: synonym: среда описания ресурса
: importance: Medium
: domain: ontology
: related: knowledge graph

Term: Individual: OWL
: SetModel: Model Term
: definition: Web Ontology Language - язык описания онтологий для семантической паутины
: synonym: язык онтологий
: importance: Medium
: domain: ontology
: related: RDF
: related: knowledge graph

Term: Individual: triples
: SetModel: Model Term
: definition: Базовая единица семантических данных: субъект-предикат-объект
: synonym: триплеты
: importance: Medium
: domain: ontology
: related: RDF
: related: OWL

Term: Individual: node
: SetModel: Model Term
: definition: Узел в графе знаний, представляющий сущность или концепт
: synonym: вершина графа
: importance: Medium
: domain: ontology

Term: Individual: edge
: SetModel: Model Term
: definition: Ребро в графе знаний, представляющее отношение между узлами
: synonym: связь в графе
: importance: Medium
: domain: ontology
: related: node

# AI и интеграция

Term: Individual: LLM
: SetModel: Model Term
: definition: Large Language Model - большая языковая модель, используемая для генерации моделей и интерфейсов в boldsea
: synonym: большая языковая модель
: importance: High
: domain: ai-интеграция

Term: Individual: prompt
: SetModel: Model Term
: definition: Запрос к LLM для извлечения фрагментов или генерации моделей
: synonym: промпт
: importance: Medium
: domain: ai-интеграция
: related: LLM

Term: Individual: RAG
: SetModel: Model Term
: definition: Retrieval-Augmented Generation - метод интеграции KG с LLM для улучшения генерации
: synonym: retrieval-augmented generation
: importance: Medium
: domain: ai-интеграция
: related: knowledge graph
: related: LLM

Term: Individual: inference
: SetModel: Model Term
: definition: Вывод новых фактов из KG с использованием семантических правил или AI
: synonym: логический вывод
: importance: High
: domain: ai-интеграция

Term: Individual: reasoning
: SetModel: Model Term
: definition: Процесс логического вывода и рассуждений в системах знаний
: synonym: рассуждение
: importance: High
: domain: ai-интеграция

# Технические процессы

Term: Individual: валидация
: SetModel: Model Term
: definition: Процесс проверки событий на соответствие ограничениям и условиям модели
: synonym: validation
: synonym: проверка
: synonym: верификация
: importance: Medium
: domain: boldsea

Term: Individual: подписка
: SetModel: Model Term
: definition: Механизм отслеживания появления новых событий для выполнения условий создания других событий
: synonym: subscription
: synonym: мониторинг событий
: importance: Medium
: domain: boldsea

Term: Individual: access control
: SetModel: Model Term
: definition: Система контроля доступа к ресурсам системы
: synonym: контроль доступа
: importance: Medium
: domain: ограничивающие свойства

Term: Individual: integration
: SetModel: Model Term
: definition: Процесс интеграции с внешними системами
: synonym: интеграция
: importance: Medium
: domain: интерфейс

# Добавляем недостающие связи после определения всех терминов

Term: Individual: boldsea
: SetModel: Model Term
: related: ontology

Term: Individual: dataflow-архитектура
: SetModel: Model Term
: synonym: event-driven architecture
: related: control flow

Term: Individual: condition
: SetModel: Model Term
: related: язык выражений

Term: Individual: permission
: SetModel: Model Term
: related: access control

Term: Individual: SetValue
: SetModel: Model Term
: related: язык запросов
: related: язык выражений

Term: Individual: BPMN
: SetModel: Model Term
: related: task
: related: sequence flow

Term: Individual: task
: SetModel: Model Term
: related: gateway

Term: Individual: knowledge graph
: SetModel: Model Term
: domain: ontology
: related: triples
: related: node
: related: edge

Term: Individual: query operator
: SetModel: Model Term
: related: язык запросов

Term: Individual: api
: SetModel: Model Term
: related: integration

Term: Individual: inference
: SetModel: Model Term
: broader: reasoning