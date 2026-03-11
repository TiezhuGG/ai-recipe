import { ref, watch, onMounted } from "vue";

const STORAGE_KEY = "recipe_form_data";

interface FormData {
  ingredients: string[]
  flavorTags: string
  cuisineTypes: string
  specialGroups: string[]
}

/**
 * 表单数据持久化 Composable
 * 只持久化口味、菜系和特殊人群，不持久化食材
 */
export function useFormPersistence() {
  const formData = ref<FormData>({
    ingredients: [],  // 不持久化
    flavorTags: '',
    cuisineTypes: '',
    specialGroups: [],
  });

  /**
   * 从 localStorage 加载保存的数据
   */
  function loadFromStorage() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        formData.value = {
          ingredients: [],  // 食材不从缓存恢复
          flavorTags: parsed.flavorTags || '',
          cuisineTypes: parsed.cuisineTypes || '',
          specialGroups: parsed.specialGroups || [],
        };
      }
    } catch (error) {
      console.error("Failed to load form data from localStorage:", error);
    }
  }

  /**
   * 保存数据到 localStorage（不保存食材）
   */
  function saveToStorage(data: FormData) {
    try {
      const dataToSave = {
        flavorTags: data.flavorTags,
        cuisineTypes: data.cuisineTypes,
        specialGroups: data.specialGroups,
        // 不保存 ingredients
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
    } catch (error) {
      console.error("Failed to save form data to localStorage:", error);
    }
  }

  /**
   * 清除保存的数据
   */
  function clearStorage() {
    try {
      localStorage.removeItem(STORAGE_KEY);
      formData.value = {
        ingredients: [],
        flavorTags: '',
        cuisineTypes: '',
        specialGroups: [],
      };
    } catch (error) {
      console.error("Failed to clear form data from localStorage:", error);
    }
  }

  // 组件挂载时加载数据
  onMounted(() => {
    loadFromStorage();
  });

  // 监听数据变化，自动保存（使用 flush: 'post' 避免递归更新）
  watch(
    () => formData.value,
    (newValue) => {
      saveToStorage(newValue);
    },
    { deep: true, flush: 'post' },
  );

  return {
    formData,
    clearStorage,
  };
}
