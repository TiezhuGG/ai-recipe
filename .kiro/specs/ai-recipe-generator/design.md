# 设计文档 - AI智能菜谱生成平台

## 概述

AI智能菜谱生成平台是一个全栈Web应用，采用前后端分离架构。前端使用Vue3 + TypeScript + Vite构建响应式用户界面，后端使用Python FastAPI提供RESTful API服务，通过豆包AI API实现智能菜谱生成和图片识别功能。系统使用SQLite/PostgreSQL存储用户数据和菜谱记录。

## 架构

### 系统架构图

```mermaid
graph TB
    subgraph "前端层 - Vue3 + TypeScript"
        UI[用户界面组件]
        Store[状态管理]
        API_Client[API客户端]
    end
    
    subgraph "后端层 - Python FastAPI"
        Router[路由层]
        Service[业务逻辑层]
        AI_Service[AI服务层]
        DB_Layer[数据访问层]
    end
    
    subgraph "外部服务"
        Doubao[豆包API]
    end
    
    subgraph "数据层"
        DB[(数据库)]
        FS[文件系统]
    end
    
    UI --> Store
    Store --> API_Client
    API_Client -->|HTTP/REST| Router
    Router --> Service
    Service --> AI_Service
    Service --> DB_Layer
    AI_Service -->|API调用| Doubao
    DB_Layer --> DB
    Service --> FS
```

### 技术栈

**前端:**
- Vue 3.x (组合式API)
- TypeScript 5.x
- Vite 5.x (构建工具)
- Axios (HTTP客户端)
- Pinia (状态管理，可选)
- TailwindCSS 或 Element Plus (UI框架)

**后端:**
- Python 3.10+
- FastAPI 0.100+
- SQLAlchemy 2.x (ORM)
- Pydantic 2.x (数据验证)
- Uvicorn (ASGI服务器)
- Python-multipart (文件上传)
- httpx (异步HTTP客户端)

**数据库:**
- SQLite (开发环境)
- PostgreSQL (生产环境)

**AI服务:**
- 豆包API (文本生成和图像识别)

## 组件和接口

### 前端组件

#### 1. RecipeGeneratorForm 组件

主要的菜谱生成表单组件，包含所有输入控件。

```typescript
interface RecipeGeneratorFormProps {
  onGenerate: (params: GenerateParams) => Promise<void>
}

interface GenerateParams {
  ingredients: string[]
  flavorTags: string[]
  cuisineTypes: string[]
  specialGroups: string[]
  uploadedImage?: File
}
```

**子组件:**
- `IngredientInput`: 食材输入框
- `FlavorSelector`: 口味标签选择器
- `CuisineSelector`: 菜系选择器
- `ImageUploader`: 图片上传组件
- `SpecialGroupSelector`: 特殊人群选择器

#### 2. RecipeDisplay 组件

显示生成的菜谱详情。

```typescript
interface RecipeDisplayProps {
  recipe: Recipe
  onSave: (recipe: Recipe) => Promise<void>
}

interface Recipe {
  id?: string
  name: string
  image?: string
  ingredients: {
    main: Ingredient[]
    secondary: Ingredient[]
  }
  steps: Step[]
  difficulty: 'easy' | 'medium' | 'hard'
  cookingTime: number // 分钟
  servings: number
  safetyTips?: string[]
  createdAt?: string
}

interface Ingredient {
  name: string
  amount: string
  unit: string
}

interface Step {
  order: number
  description: string
  image?: string
}
```

#### 3. RecipeHistory 组件

显示用户的历史菜谱列表。

```typescript
interface RecipeHistoryProps {
  onSelectRecipe: (recipeId: string) => void
}

interface RecipeListItem {
  id: string
  name: string
  thumbnail?: string
  createdAt: string
  difficulty: string
}
```

#### 4. API客户端服务

```typescript
class RecipeAPIClient {
  private baseURL: string
  private httpClient: AxiosInstance

  async generateRecipe(params: GenerateRecipeRequest): Promise<Recipe>
  async uploadImage(file: File): Promise<ImageRecognitionResponse>
  async saveRecipe(recipe: Recipe): Promise<SaveRecipeResponse>
  async getRecipeHistory(): Promise<RecipeListItem[]>
  async getRecipeById(id: string): Promise<Recipe>
}

interface GenerateRecipeRequest {
  ingredients: string[]
  flavorTags: string[]
  cuisineTypes: string[]
  specialGroups: string[]
  recognizedIngredients?: string[]
}

interface ImageRecognitionResponse {
  ingredients: string[]
  confidence: number
}

interface SaveRecipeResponse {
  id: string
  success: boolean
}
```

### 后端API端点

#### 1. 菜谱生成端点

```python
@router.post("/api/recipes/generate")
async def generate_recipe(
    request: GenerateRecipeRequest,
    session_id: str = Cookie(None)
) -> RecipeResponse:
    """
    生成AI菜谱
    
    参数:
        request: 包含食材、口味、菜系等信息的请求体
        session_id: 用户会话ID（从Cookie获取）
    
    返回:
        RecipeResponse: 生成的菜谱数据
    
    异常:
        400: 请求参数无效
        500: AI服务调用失败
    """
    pass
```

**请求模型:**
```python
class GenerateRecipeRequest(BaseModel):
    ingredients: List[str] = Field(min_length=1)
    flavor_tags: List[str] = []
    cuisine_types: List[str] = []
    special_groups: List[str] = []
    recognized_ingredients: Optional[List[str]] = None
```

**响应模型:**
```python
class RecipeResponse(BaseModel):
    name: str
    image: Optional[str]
    ingredients: RecipeIngredients
    steps: List[RecipeStep]
    difficulty: Literal["easy", "medium", "hard"]
    cooking_time: int
    servings: int
    safety_tips: Optional[List[str]]

class RecipeIngredients(BaseModel):
    main: List[Ingredient]
    secondary: List[Ingredient]

class Ingredient(BaseModel):
    name: str
    amount: str
    unit: str

class RecipeStep(BaseModel):
    order: int
    description: str
    image: Optional[str]
```

#### 2. 图片上传和识别端点

```python
@router.post("/api/images/recognize")
async def recognize_ingredients(
    file: UploadFile = File(...)
) -> ImageRecognitionResponse:
    """
    上传图片并识别食材
    
    参数:
        file: 上传的图片文件
    
    返回:
        ImageRecognitionResponse: 识别的食材列表
    
    异常:
        400: 文件格式不支持或文件过大
        500: AI识别服务失败
    """
    pass
```

**响应模型:**
```python
class ImageRecognitionResponse(BaseModel):
    ingredients: List[str]
    confidence: float
```

#### 3. 菜谱保存端点

```python
@router.post("/api/recipes/save")
async def save_recipe(
    recipe: SaveRecipeRequest,
    session_id: str = Cookie(None)
) -> SaveRecipeResponse:
    """
    保存菜谱到用户历史
    
    参数:
        recipe: 要保存的菜谱数据
        session_id: 用户会话ID
    
    返回:
        SaveRecipeResponse: 保存结果和菜谱ID
    
    异常:
        400: 菜谱数据无效
        500: 数据库保存失败
    """
    pass
```

#### 4. 历史菜谱查询端点

```python
@router.get("/api/recipes/history")
async def get_recipe_history(
    session_id: str = Cookie(None),
    limit: int = 50,
    offset: int = 0
) -> RecipeHistoryResponse:
    """
    获取用户的历史菜谱列表
    
    参数:
        session_id: 用户会话ID
        limit: 返回数量限制
        offset: 分页偏移量
    
    返回:
        RecipeHistoryResponse: 菜谱列表
    """
    pass
```

```python
@router.get("/api/recipes/{recipe_id}")
async def get_recipe_by_id(
    recipe_id: str,
    session_id: str = Cookie(None)
) -> RecipeResponse:
    """
    根据ID获取菜谱详情
    
    参数:
        recipe_id: 菜谱ID
        session_id: 用户会话ID
    
    返回:
        RecipeResponse: 菜谱详情
    
    异常:
        404: 菜谱不存在
        403: 无权访问该菜谱
    """
    pass
```

### 后端服务层

#### 1. AIService - AI服务

```python
class AIService:
    """处理与豆包API的交互"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def generate_recipe(
        self,
        ingredients: List[str],
        flavor_tags: List[str],
        cuisine_types: List[str],
        special_groups: List[str]
    ) -> Dict[str, Any]:
        """
        调用豆包API生成菜谱
        
        构建提示词，调用AI生成菜谱内容
        实现重试机制（最多2次）
        """
        pass
    
    async def recognize_ingredients(
        self,
        image_path: str
    ) -> List[str]:
        """
        调用豆包API识别图片中的食材
        
        上传图片到AI服务
        解析识别结果
        """
        pass
    
    def _build_recipe_prompt(
        self,
        ingredients: List[str],
        flavor_tags: List[str],
        cuisine_types: List[str],
        special_groups: List[str]
    ) -> str:
        """构建菜谱生成的提示词"""
        pass
    
    def _parse_recipe_response(
        self,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """解析AI返回的菜谱数据"""
        pass
```

#### 2. RecipeService - 菜谱业务逻辑

```python
class RecipeService:
    """处理菜谱相关的业务逻辑"""
    
    def __init__(
        self,
        ai_service: AIService,
        recipe_repository: RecipeRepository
    ):
        self.ai_service = ai_service
        self.recipe_repository = recipe_repository
    
    async def generate_recipe(
        self,
        params: GenerateRecipeRequest,
        user_id: str
    ) -> Recipe:
        """
        生成菜谱的完整流程
        
        1. 验证输入参数
        2. 调用AI服务生成菜谱
        3. 添加特殊人群安全提示
        4. 返回结构化菜谱数据
        """
        pass
    
    async def save_recipe(
        self,
        recipe: Recipe,
        user_id: str
    ) -> str:
        """
        保存菜谱到数据库
        
        返回菜谱ID
        """
        pass
    
    async def get_user_recipes(
        self,
        user_id: str,
        limit: int,
        offset: int
    ) -> List[Recipe]:
        """获取用户的历史菜谱"""
        pass
    
    async def get_recipe_by_id(
        self,
        recipe_id: str,
        user_id: str
    ) -> Optional[Recipe]:
        """根据ID获取菜谱，验证用户权限"""
        pass
    
    def _add_safety_tips(
        self,
        recipe: Recipe,
        special_groups: List[str]
    ) -> Recipe:
        """根据特殊人群添加安全提示"""
        pass
```

#### 3. ImageService - 图片处理服务

```python
class ImageService:
    """处理图片上传和存储"""
    
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
    
    async def save_uploaded_image(
        self,
        file: UploadFile
    ) -> str:
        """
        保存上传的图片
        
        1. 验证文件格式
        2. 验证文件大小
        3. 生成唯一文件名
        4. 保存到文件系统
        5. 返回文件路径
        """
        pass
    
    def validate_image(self, file: UploadFile) -> bool:
        """验证图片格式和大小"""
        pass
    
    def generate_filename(self, original_filename: str) -> str:
        """生成唯一的文件名"""
        pass
```

#### 4. SessionService - 会话管理服务

```python
class SessionService:
    """处理用户会话"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def get_or_create_user(
        self,
        session_id: Optional[str]
    ) -> Tuple[str, str]:
        """
        获取或创建用户会话
        
        返回: (user_id, session_id)
        """
        pass
    
    def generate_session_id(self) -> str:
        """生成唯一的会话ID"""
        pass
```

## 数据模型

### 数据库Schema

```python
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    recipes = relationship("Recipe", back_populates="user", cascade="all, delete-orphan")

class Recipe(Base):
    """菜谱表"""
    __tablename__ = "recipes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    image = Column(String(500), nullable=True)
    
    # 使用JSON存储复杂结构
    ingredients = Column(JSON, nullable=False)  # {main: [...], secondary: [...]}
    steps = Column(JSON, nullable=False)  # [{order, description, image}, ...]
    
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    cooking_time = Column(Integer, nullable=False)  # 分钟
    servings = Column(Integer, nullable=False)
    safety_tips = Column(JSON, nullable=True)  # [tip1, tip2, ...]
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 关系
    user = relationship("User", back_populates="recipes")
```

### 数据访问层

```python
class UserRepository:
    """用户数据访问"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def create_user(self, session_id: str) -> User:
        """创建新用户"""
        pass
    
    async def get_by_session_id(self, session_id: str) -> Optional[User]:
        """根据会话ID查询用户"""
        pass

class RecipeRepository:
    """菜谱数据访问"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def create(self, recipe_data: Dict[str, Any], user_id: str) -> Recipe:
        """创建菜谱记录"""
        pass
    
    async def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """根据ID查询菜谱"""
        pass
    
    async def get_by_user(
        self,
        user_id: str,
        limit: int,
        offset: int
    ) -> List[Recipe]:
        """查询用户的菜谱列表"""
        pass
    
    async def delete(self, recipe_id: str) -> bool:
        """删除菜谱"""
        pass
```

## 正确性属性

*正确性属性是系统应该在所有有效执行中保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*


### 属性 1: 食材输入解析一致性

*对于任何*逗号分隔的食材字符串，解析后的食材数组长度应该等于逗号数量加1（假设没有连续逗号），且每个食材应该去除前后空白。

**验证需求: 1.2**

### 属性 2: 空白输入拒绝

*对于任何*仅包含空白字符（空格、制表符、换行符等）的字符串，食材验证函数应该返回false并阻止提交。

**验证需求: 1.3**

### 属性 3: 食材列表操作不变性

*对于任何*食材列表，添加一个食材后再删除该食材，应该返回到原始状态（列表长度和内容相同）。

**验证需求: 1.4**

### 属性 4: 选择状态切换幂等性

*对于任何*选项（口味标签或菜系），点击两次应该返回到初始状态（选中→未选中→选中 或 未选中→选中→未选中）。

**验证需求: 2.3**

### 属性 5: 多选状态累积

*对于任何*一组选项，依次选择多个选项后，所有被选择的选项都应该处于选中状态。

**验证需求: 2.4, 2.5**

### 属性 6: 偏好设置往返一致性

*对于任何*有效的偏好设置（口味和菜系），提交到后端后再查询，应该得到相同的偏好设置。

**验证需求: 2.6**

### 属性 7: 图片格式验证

*对于任何*文件，如果其扩展名是JPEG、PNG或WebP（不区分大小写），验证函数应该返回true；否则返回false。

**验证需求: 3.2**

### 属性 8: 图片上传存储可检索性

*对于任何*有效的图片文件，上传并保存后，应该能够通过返回的文件路径访问到该文件。

**验证需求: 3.4**

### 属性 9: 识别食材自动填充

*对于任何*从图片识别返回的食材列表，前端接收后应该将这些食材添加到当前食材输入区域，且不覆盖已有食材。

**验证需求: 3.7**

### 属性 10: 特殊人群安全提示存在性

*对于任何*包含特殊人群选择的菜谱生成请求，返回的菜谱应该包含非空的安全提示数组。

**验证需求: 4.3**

### 属性 11: 生成请求参数验证

*对于任何*菜谱生成请求，如果食材列表为空且没有上传图片，验证函数应该返回错误；如果至少有一个非空，应该通过验证。

**验证需求: 5.1, 5.2**

### 属性 12: 提示词包含所有输入信息

*对于任何*有效的生成请求，构建的提示词字符串应该包含所有提供的食材名称、所有选择的口味标签和菜系类型。

**验证需求: 5.3**

### 属性 13: 菜谱解析完整性

*对于任何*从AI返回的菜谱数据，解析后的结构化菜谱对象应该包含所有必需字段：name、ingredients、steps、difficulty、cooking_time、servings。

**验证需求: 5.5, 5.7**

### 属性 14: 菜谱渲染完整性

*对于任何*有效的菜谱对象，渲染后的HTML应该包含菜名、所有食材（分类显示）、所有步骤（按顺序）、难度、时间和人数信息。

**验证需求: 6.1, 6.3, 6.4, 6.5**

### 属性 15: 条件内容显示

*对于任何*菜谱对象，如果image字段非空，渲染应该包含图片元素；如果safety_tips非空，渲染应该包含安全提示区域。

**验证需求: 6.2, 6.6**

### 属性 16: 菜谱保存和检索往返一致性

*对于任何*有效的菜谱对象，保存到数据库后通过返回的ID查询，应该得到包含相同核心信息（name、ingredients、steps、difficulty等）的菜谱对象。

**验证需求: 7.2, 7.3, 7.5, 7.6**

### 属性 17: 用户菜谱隔离性

*对于任何*两个不同的用户会话，用户A保存的菜谱不应该出现在用户B的历史记录查询结果中。

**验证需求: 7.5, 8.5**

### 属性 18: 会话标识唯一性

*对于任何*两次独立的首次访问，生成的会话标识应该是不同的。

**验证需求: 8.1**

### 属性 19: 会话验证正确性

*对于任何*有效的会话标识，验证函数应该返回true并找到对应的用户；对于无效或不存在的会话标识，应该返回false或创建新会话。

**验证需求: 8.3, 8.4**

### 属性 20: API重试机制

*对于任何*模拟的API失败场景，如果配置了最多2次重试，系统应该总共尝试3次调用（1次初始 + 2次重试）后才返回失败。

**验证需求: 9.6**

### 属性 21: API错误处理友好性

*对于任何*来自豆包API的错误响应（超时、错误状态码、解析失败），后端应该返回包含友好错误消息的响应，而不是抛出未捕获的异常。

**验证需求: 9.3, 9.4, 9.5**

### 属性 22: 数据库关联完整性

*对于任何*保存的菜谱，通过菜谱的user_id应该能够查询到对应的用户记录，且该用户的recipes关系应该包含该菜谱。

**验证需求: 10.4**

### 属性 23: 前端加载状态一致性

*对于任何*API请求，在请求开始时loading状态应该为true，在请求完成（成功或失败）后loading状态应该为false。

**验证需求: 11.3, 11.4**

### 属性 24: 前端错误状态设置

*对于任何*失败的API请求，前端应该设置error状态为非空值，且该值应该包含可显示的错误信息。

**验证需求: 11.5**

### 属性 25: 输入数据持久化

*对于任何*用户在表单中输入的数据，如果用户导航离开页面，数据应该保存到localStorage；当用户返回时，应该能够恢复这些数据。

**验证需求: 11.6**

## 错误处理

### 前端错误处理

1. **网络错误**: 捕获所有API请求的网络错误，显示友好的错误提示
2. **验证错误**: 在提交前验证所有输入，显示具体的验证错误信息
3. **文件上传错误**: 验证文件类型和大小，显示清晰的错误原因
4. **状态错误**: 使用try-catch包裹状态更新逻辑，防止应用崩溃

### 后端错误处理

1. **请求验证错误**: 使用Pydantic自动验证请求体，返回422状态码和详细错误信息
2. **AI服务错误**: 
   - 超时: 返回504状态码和超时提示
   - API错误: 记录日志，返回500状态码和通用错误信息
   - 解析错误: 返回默认菜谱或错误提示
3. **数据库错误**: 
   - 连接失败: 应用启动时检查，启动失败
   - 查询失败: 记录日志，返回500状态码
   - 约束违反: 返回400状态码和具体错误
4. **文件系统错误**: 
   - 磁盘空间不足: 返回507状态码
   - 权限错误: 记录日志，返回500状态码
5. **会话错误**: 无效会话自动创建新会话，不返回错误

### 错误日志

使用Python logging模块记录所有错误：
- ERROR级别: 系统错误、外部服务失败
- WARNING级别: 验证失败、用户输入错误
- INFO级别: 正常操作日志

## 测试策略

### 单元测试

**前端单元测试 (Vitest + Vue Test Utils):**
- 组件渲染测试: 验证组件正确渲染
- 用户交互测试: 模拟点击、输入等操作
- 状态管理测试: 验证状态更新逻辑
- API客户端测试: 使用mock验证API调用

**后端单元测试 (pytest):**
- API端点测试: 使用TestClient测试所有端点
- 服务层测试: 测试业务逻辑，mock外部依赖
- 数据访问层测试: 使用内存数据库测试CRUD操作
- 工具函数测试: 测试提示词构建、数据解析等

### 属性测试

**前端属性测试 (fast-check):**
- 每个属性测试运行最少100次迭代
- 使用随机生成器生成测试数据
- 测试标签格式: `Feature: ai-recipe-generator, Property {N}: {property_text}`

**后端属性测试 (Hypothesis):**
- 每个属性测试运行最少100次迭代
- 使用Hypothesis策略生成测试数据
- 测试标签格式: `Feature: ai-recipe-generator, Property {N}: {property_text}`

### 集成测试

- 前后端集成: 使用真实HTTP请求测试完整流程
- 数据库集成: 使用测试数据库验证数据持久化
- AI服务集成: 使用mock或测试API密钥验证集成

### 测试覆盖率目标

- 单元测试覆盖率: 80%以上
- 属性测试: 覆盖所有25个正确性属性
- 集成测试: 覆盖所有主要用户流程

### 测试数据生成

**前端 (fast-check):**
```typescript
import fc from 'fast-check'

// 生成食材列表
const ingredientArb = fc.array(fc.string({ minLength: 1, maxLength: 20 }), { minLength: 1, maxLength: 10 })

// 生成菜谱对象
const recipeArb = fc.record({
  name: fc.string({ minLength: 1, maxLength: 100 }),
  ingredients: fc.record({
    main: fc.array(ingredientArb),
    secondary: fc.array(ingredientArb)
  }),
  steps: fc.array(fc.record({
    order: fc.nat(),
    description: fc.string({ minLength: 1 })
  })),
  difficulty: fc.constantFrom('easy', 'medium', 'hard'),
  cooking_time: fc.integer({ min: 5, max: 300 }),
  servings: fc.integer({ min: 1, max: 10 })
})
```

**后端 (Hypothesis):**
```python
from hypothesis import strategies as st

# 生成食材列表
ingredients_strategy = st.lists(
    st.text(min_size=1, max_size=20),
    min_size=1,
    max_size=10
)

# 生成菜谱对象
recipe_strategy = st.builds(
    Recipe,
    name=st.text(min_size=1, max_size=100),
    difficulty=st.sampled_from(['easy', 'medium', 'hard']),
    cooking_time=st.integers(min_value=5, max_value=300),
    servings=st.integers(min_value=1, max_value=10)
)
```

## 部署考虑

### 开发环境

- 前端: `npm run dev` (Vite开发服务器，端口3000)
- 后端: `uvicorn main:app --reload` (端口8000)
- 数据库: SQLite文件 `dev.db`
- 环境变量: `.env.development`

### 生产环境

- 前端: 构建静态文件，部署到CDN或静态托管服务
- 后端: 使用Gunicorn + Uvicorn workers，部署到云服务器
- 数据库: PostgreSQL，独立数据库服务器
- 反向代理: Nginx，处理静态文件和API路由
- HTTPS: 使用Let's Encrypt证书
- 环境变量: 使用环境变量或密钥管理服务

### 环境变量

```bash
# 后端环境变量
DOUBAO_API_KEY=your_api_key_here
DOUBAO_API_BASE_URL=https://api.doubao.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
UPLOAD_DIR=/var/uploads
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=https://yourdomain.com

# 前端环境变量
VITE_API_BASE_URL=https://api.yourdomain.com
```

## 性能优化

### 前端优化

1. **代码分割**: 使用Vue Router的懒加载
2. **图片优化**: 使用WebP格式，实现懒加载
3. **缓存策略**: 缓存历史菜谱列表
4. **防抖节流**: 对输入事件使用防抖

### 后端优化

1. **数据库索引**: 在user_id、session_id、created_at字段上建立索引
2. **连接池**: 使用SQLAlchemy连接池
3. **缓存**: 使用Redis缓存频繁查询的数据
4. **异步处理**: 使用FastAPI的异步特性
5. **文件存储**: 考虑使用对象存储服务（如S3）

## 安全考虑

1. **输入验证**: 所有用户输入都经过验证和清理
2. **SQL注入防护**: 使用ORM参数化查询
3. **XSS防护**: 前端对用户输入进行转义
4. **CSRF防护**: 使用SameSite Cookie属性
5. **文件上传安全**: 验证文件类型，限制文件大小，使用随机文件名
6. **API密钥保护**: 密钥存储在环境变量中，不提交到代码仓库
7. **HTTPS**: 生产环境强制使用HTTPS
8. **速率限制**: 对API端点实施速率限制，防止滥用
