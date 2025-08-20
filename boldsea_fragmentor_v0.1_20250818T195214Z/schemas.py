from __future__ import annotations
from enum import Enum
from typing import Dict

class SchemaType(str, Enum):
    # Basic
    DEFINITION = "Definition"
    COMPARISON = "Comparison"
    CAUSAL_RELATION = "Causal Relation"
    APPLICATION_CONTEXT = "Application Context"
    EXAMPLE = "Example"
    # Architectural/Technical
    ARCHITECTURAL_COMPONENT = "Architectural Component"
    TECHNICAL_PROCESS = "Technical Process"
    ALGORITHM = "Algorithm"
    # Conceptual
    CONCEPTUAL_MODEL = "Conceptual Model"
    PRINCIPLE = "Principle"
    # Problem-oriented
    PROBLEM_SOLUTION = "Problem Solution"
    LIMITATIONS_AND_CHALLENGES = "Limitations And Challenges"
    # Functional
    FUNCTIONALITY = "Functionality"
    CAPABILITIES = "Capabilities"
    # Integration
    SYSTEM_INTEGRATION = "System Integration"
    COMPONENT_INTERACTION = "Component Interaction"
    # Applied
    USE_CASE = "Use Case"
    CONCEPT_IMPLEMENTATION = "Concept Implementation"
    CODE_SNIPPET = "Code Snippet"
    ENUMERATION = "Enumeration"
    TABLE_ANALYSIS = "Table Analysis"
    ADVANTAGE_DISADVANTAGE = "Advantage Disadvantage"
    # Fallback
    UNKNOWN = "Unknown"

SCHEMA_INSTRUCTIONS: Dict[str, Dict[str, str]] = {
    SchemaType.DEFINITION.value: {
        "display_name": "Определение",
        "llm_prompt_template": "Извлеки из определения: term (определяемый термин), includes (термины, упомянутые в определении)",
        "extraction_fields": '{"term": "Range: Term", "includes": "Range: Term, Multiple: 1"}',
    },
    SchemaType.COMPARISON.value: {
        "display_name": "Сравнение",
        "llm_prompt_template": "Извлеки из сравнения: target (основной объект сравнения), comparator (с чем сравнивается), criterion (критерии сравнения), advantage (у кого преимущество по каждому критерию)",
        "extraction_fields": '{"target": "Range: Term", "comparator": "Range: Term", "criterion": "Range: Term, Multiple: 1", "advantage": "SetRange: [target, comparator]"}',
    },
    SchemaType.CAUSAL_RELATION.value: {
        "display_name": "Причинно-следственная связь",
        "llm_prompt_template": "Извлеки причинно-следственные связи: cause (причины, факторы влияния), effect (следствия, результаты)",
        "extraction_fields": '{"cause": "Range: Term, Multiple: 1", "effect": "Range: Term, Multiple: 1"}',
    },
    SchemaType.APPLICATION_CONTEXT.value: {
        "display_name": "Контекст применения",
        "llm_prompt_template": "Извлеки контекст применения: domain (область применения)",
        "extraction_fields": '{"domain": "Range: Term, Multiple: 1"}',
    },
    SchemaType.EXAMPLE.value: {
        "display_name": "Пример",
        "llm_prompt_template": "Извлеки из примера: illustrates (что иллюстрирует), type (тип примера: code/scenario/analogy/counter-example)",
        "extraction_fields": '{"illustrates": "Range: Term, Multiple: 1", "type": "DataType: EnumType"}',
    },
    SchemaType.ARCHITECTURAL_COMPONENT.value: {
        "display_name": "Архитектурный компонент",
        "llm_prompt_template": "Извлеки компонент системы: system_terms (к какой системе относится), purpose_terms (назначение), interfaces_terms (с чем взаимодействует), pattern_terms (архитектурные паттерны)",
        "extraction_fields": '{"system_terms": "Range: Term, Multiple: 1", "purpose_terms": "Range: Term, Multiple: 1", "interfaces_terms": "Range: Term, Multiple: 1", "pattern_terms": "Range: Term, Multiple: 1"}',
    },
    SchemaType.TECHNICAL_PROCESS.value: {
        "display_name": "Технический процесс",
        "llm_prompt_template": "Извлеки технический процесс: input_types (типы входных данных), output_types (типы выходных данных), process_category (категория процесса), involves_components (задействованные компоненты)",
        "extraction_fields": '{"input_types": "Range: Term, Multiple: 1", "output_types": "Range: Term, Multiple: 1", "process_category": "Range: Term", "involves_components": "Range: Term, Multiple: 1"}',
    },
    SchemaType.ALGORITHM.value: {
        "display_name": "Алгоритм/Метод",
        "llm_prompt_template": "Извлеки алгоритм: input_types (типы входных данных), output_types (результаты), involves_components (используемые концепты), process_category (тип алгоритма)",
        "extraction_fields": '{"input_types": "Range: Term, Multiple: 1", "output_types": "Range: Term, Multiple: 1", "involves_components": "Range: Term, Multiple: 1", "process_category": "Range: Term"}',
    },
    SchemaType.CONCEPTUAL_MODEL.value: {
        "display_name": "Концептуальная модель",
        "llm_prompt_template": "Извлеки концептуальную модель: target (центральный концепт), involves_components (связанные концепты)",
        "extraction_fields": '{"target": "Range: Term", "involves_components": "Range: Term, Multiple: 1"}',
    },
    SchemaType.PRINCIPLE.value: {
        "display_name": "Принцип/Подход",
        "llm_prompt_template": "Извлеки принцип: target (принцип/подход), domain (к чему применяется), comparator (с чем контрастирует), demonstrates (что обеспечивает)",
        "extraction_fields": '{"target": "Range: Term", "domain": "Range: Term, Multiple: 1", "comparator": "Range: Term, Multiple: 1", "demonstrates": "Range: Term, Multiple: 1"}',
    },
    SchemaType.PROBLEM_SOLUTION.value: {
        "display_name": "Проблема и решение",
        "llm_prompt_template": "Извлеки проблему и решение: problem_domain (область проблемы), solution_components (компоненты решения)",
        "extraction_fields": '{"problem_domain": "Range: Term, Multiple: 1", "solution_components": "Range: Term, Multiple: 1"}',
    },
    SchemaType.LIMITATIONS_AND_CHALLENGES.value: {
        "display_name": "Ограничения и вызовы",
        "llm_prompt_template": "Извлеки ограничения: target (к чему относится), problem_domain (тип ограничения/проблемы)",
        "extraction_fields": '{"target": "Range: Term", "problem_domain": "Range: Term, Multiple: 1"}',
    },
    SchemaType.FUNCTIONALITY.value: {
        "display_name": "Функциональность",
        "llm_prompt_template": "Извлеки функциональность: system_terms (система/компонент), purpose_terms (функции), involves_components (зависимости)",
        "extraction_fields": '{"system_terms": "Range: Term", "purpose_terms": "Range: Term, Multiple: 1", "involves_components": "Range: Term, Multiple: 1"}',
    },
    SchemaType.CAPABILITIES.value: {
        "display_name": "Возможности",
        "llm_prompt_template": "Извлеки возможности: target (что обладает возможностями), purpose_terms (типы возможностей), demonstrates (какие сценарии обеспечивает)",
        "extraction_fields": '{"target": "Range: Term", "purpose_terms": "Range: Term, Multiple: 1", "demonstrates": "Range: Term, Multiple: 1"}',
    },
    SchemaType.SYSTEM_INTEGRATION.value: {
        "display_name": "Интеграция систем",
        "llm_prompt_template": "Извлеки интеграцию: target (основная система), comparator (интегрируемая система), interfaces_terms (точки интеграции), process_category (метод интеграции)",
        "extraction_fields": '{"target": "Range: Term", "comparator": "Range: Term", "interfaces_terms": "Range: Term, Multiple: 1", "process_category": "Range: Term"}',
    },
    SchemaType.COMPONENT_INTERACTION.value: {
        "display_name": "Взаимодействие компонентов",
        "llm_prompt_template": "Извлеки взаимодействие: target (инициатор), comparator (цель взаимодействия), process_category (тип взаимодействия), involves_components (посредники)",
        "extraction_fields": '{"target": "Range: Term", "comparator": "Range: Term", "process_category": "Range: Term", "involves_components": "Range: Term, Multiple: 1"}',
    },
    SchemaType.USE_CASE.value: {
        "display_name": "Сценарий использования",
        "llm_prompt_template": "Извлеки сценарий: domain (предметная область), actors (участники), demonstrates (что демонстрирует)",
        "extraction_fields": '{"domain": "Range: Term", "actors": "Range: Term, Multiple: 1", "demonstrates": "Range: Term, Multiple: 1"}',
    },
    SchemaType.CONCEPT_IMPLEMENTATION.value: {
        "display_name": "Реализация концепции",
        "llm_prompt_template": "Извлеки реализацию: concept_ref (реализуемый концепт), technologies (используемые технологии), key_features (ключевые особенности)",
        "extraction_fields": '{"concept_ref": "Range: Term", "technologies": "Range: Term, Multiple: 1", "key_features": "Range: Term, Multiple: 1"}',
    },
    SchemaType.CODE_SNIPPET.value: {
        "display_name": "Фрагмент кода",
        "llm_prompt_template": "Extract only if fragment contains actual code/script/grammar. Извлеки код: language (язык программирования/формат), illustrates (что демонстрирует), input_types (входные параметры), output_types (выходные значения), keywords (ключевые термины)",
        "extraction_fields": '{"language": "Range: Term", "illustrates": "Range: Term, Multiple: 1", "input_types": "Range: Term, Multiple: 1", "output_types": "Range: Term, Multiple: 1", "keywords": "Range: Term, Multiple: 1"}',
    },
    SchemaType.ENUMERATION.value: {
        "display_name": "Перечисление/Список",
        "llm_prompt_template": "Extract only if fragment is a clear list/enumeration. Извлеки список: category (тип/тема списка), items (элементы списка как термины), keywords (ключевые термины)",
        "extraction_fields": '{"category": "Range: Term", "items": "Range: Term, Multiple: 1", "keywords": "Range: Term, Multiple: 1"}',
    },
    SchemaType.TABLE_ANALYSIS.value: {
        "display_name": "Таблица/Матрица",
        "llm_prompt_template": "Extract only if fragment contains structured table/matrix. Извлеки таблицу: rows (строки как термины), columns (столбцы как термины), values (значения на пересечениях), keywords (ключевые термины)",
        "extraction_fields": '{"rows": "Range: Term, Multiple: 1", "columns": "Range: Term, Multiple: 1", "values": "Range: Term, Multiple: 1", "keywords": "Range: Term, Multiple: 1"}',
    },
    SchemaType.ADVANTAGE_DISADVANTAGE.value: {
        "display_name": "Преимущества и недостатки",
        "llm_prompt_template": "Extract only if fragment clearly lists pros/cons. Извлеки: target (объект анализа), advantages (преимущества как термины), disadvantages (недостатки как термины), keywords (ключевые термины)",
        "extraction_fields": '{"target": "Range: Term", "advantages": "Range: Term, Multiple: 1", "disadvantages": "Range: Term, Multiple: 1", "keywords": "Range: Term, Multiple: 1"}',
    },
    SchemaType.UNKNOWN.value: {
        "display_name": "Неопределено",
        "llm_prompt_template": "",
        "extraction_fields": "{}",
    },
}
