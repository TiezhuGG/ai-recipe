# UI改进说明

## 改进内容

### 1. 菜系选择不再默认选中

#### 问题
- 用户打开页面时，口味偏好和菜系选择会自动从localStorage恢复上次的选择
- 这可能不是用户想要的，应该让用户每次都主动选择

#### 解决方案
修改 `useFormPersistence.ts`，不再从localStorage恢复口味和菜系的选择：

```typescript
function loadFromStorage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      formData.value = {
        ingredients: [],  // 食材不从缓存恢复
        flavorTags: '',  // 不从缓存恢复，让用户自行选择
        cuisineTypes: '',  // 不从缓存恢复，让用户自行选择
        specialGroups: parsed.specialGroups || [],  // 特殊人群仍然恢复
      };
    }
  } catch (error) {
    console.error("Failed to load form data from localStorage:", error);
  }
}
```

#### 效果
- ✅ 每次打开页面，口味和菜系都是未选中状态
- ✅ 用户需要主动选择
- ✅ 特殊人群设置仍然会保留（因为这是用户的长期偏好）

### 2. 菜谱详情页不显示保存按钮

#### 问题
- 菜谱全集中的菜谱都是已经保存到数据库的
- 点击进入详情页后，仍然显示"保存菜谱"按钮
- 这是不合理的，已保存的菜谱不应该再显示保存按钮

#### 解决方案

##### 2.1 修改RecipeDisplay组件
添加 `showSaveButton` prop，控制是否显示保存按钮：

```vue
<script setup lang="ts">
// Props
interface Props {
  recipe: Recipe | null
  showSaveButton?: boolean  // 是否显示保存按钮，默认true
}

const props = withDefaults(defineProps<Props>(), {
  showSaveButton: true
})
</script>

<template>
  <!-- 保存按钮 -->
  <button
    v-if="showSaveButton"
    @click="handleSave"
    :disabled="saving"
    class="..."
  >
    {{ saving ? '保存中...' : '💾 保存菜谱' }}
  </button>
</template>
```

##### 2.2 修改RecipeDetailView
传入 `show-save-button="false"` 隐藏保存按钮：

```vue
<template>
  <RecipeDisplay 
    v-else 
    :recipe="recipe" 
    :show-save-button="false" 
    @saved="handleRecipeSaved" 
  />
</template>
```

#### 效果
- ✅ 主页生成菜谱：显示保存按钮 ✓
- ✅ 美食盲盒生成菜谱：显示保存按钮 ✓
- ✅ 菜谱详情页（已保存）：不显示保存按钮 ✓

## 使用场景对比

### 场景1：主页生成菜谱
```vue
<!-- HomeView.vue -->
<RecipeDisplay 
  :recipe="generatedRecipe"
  @saved="handleRecipeSaved"
/>
<!-- showSaveButton 默认为 true，显示保存按钮 -->
```

### 场景2：美食盲盒生成菜谱
```vue
<!-- BlindBoxView.vue -->
<RecipeDisplay 
  :recipe="generatedRecipe"
  @saved="handleRecipeSaved"
/>
<!-- showSaveButton 默认为 true，显示保存按钮 -->
```

### 场景3：菜谱详情页（已保存）
```vue
<!-- RecipeDetailView.vue -->
<RecipeDisplay 
  :recipe="recipe"
  :show-save-button="false"
  @saved="handleRecipeSaved"
/>
<!-- 明确设置为 false，不显示保存按钮 -->
```

## 修改的文件

1. `frontend/src/composables/useFormPersistence.ts`
   - 修改 `loadFromStorage()` 方法
   - 不再恢复口味和菜系的选择

2. `frontend/src/components/RecipeDisplay.vue`
   - 添加 `showSaveButton` prop
   - 使用 `v-if` 条件渲染保存按钮

3. `frontend/src/views/RecipeDetailView.vue`
   - 传入 `:show-save-button="false"`
   - 隐藏保存按钮

## 用户体验改进

### 改进1：更清晰的选择流程
- **之前**：打开页面就有默认选择，用户可能不知道这是上次的选择
- **现在**：每次都是空白状态，用户明确知道需要自己选择

### 改进2：避免重复保存
- **之前**：已保存的菜谱仍显示保存按钮，可能导致重复保存
- **现在**：已保存的菜谱不显示保存按钮，逻辑更清晰

### 改进3：更好的语义化
- **新菜谱**：显示"保存菜谱"按钮 → 表示这是新生成的，需要保存
- **已保存菜谱**：不显示按钮 → 表示这已经在数据库中了

## 技术细节

### Props默认值
使用 `withDefaults` 设置默认值：

```typescript
const props = withDefaults(defineProps<Props>(), {
  showSaveButton: true  // 默认显示，保持向后兼容
})
```

### 条件渲染
使用 `v-if` 而不是 `v-show`：

```vue
<button v-if="showSaveButton" ...>
  保存菜谱
</button>
```

原因：
- `v-if` 完全不渲染DOM元素
- `v-show` 只是隐藏（display: none）
- 对于不需要频繁切换的元素，`v-if` 更合适

## 测试建议

### 测试1：菜系选择
1. 打开主页
2. 选择口味和菜系
3. 刷新页面
4. 验证：口味和菜系应该是未选中状态 ✓

### 测试2：保存按钮显示
1. 在主页生成菜谱
2. 验证：显示"保存菜谱"按钮 ✓
3. 点击保存
4. 进入菜谱全集
5. 点击查看该菜谱
6. 验证：不显示"保存菜谱"按钮 ✓

### 测试3：美食盲盒
1. 进入美食盲盒
2. 生成菜谱
3. 验证：显示"保存菜谱"按钮 ✓
4. 点击保存
5. 从菜谱全集查看
6. 验证：不显示"保存菜谱"按钮 ✓

## 注意事项

1. **向后兼容**：`showSaveButton` 默认为 `true`，不影响现有代码
2. **特殊人群**：仍然会从localStorage恢复，因为这是用户的长期偏好
3. **食材**：从一开始就不会缓存，保持不变

## 未来优化建议

### 1. 添加"编辑"功能
在菜谱详情页可以添加"编辑"按钮，允许用户修改已保存的菜谱

### 2. 添加"删除"功能
在菜谱详情页添加"删除"按钮，允许用户删除不需要的菜谱

### 3. 添加"收藏"功能
区分"保存"和"收藏"，保存是所有生成的菜谱，收藏是用户特别喜欢的

### 4. 添加"分享"功能
允许用户分享菜谱给朋友

### 5. 偏好设置页面
创建一个专门的设置页面，让用户管理所有偏好（包括是否记住口味和菜系选择）
