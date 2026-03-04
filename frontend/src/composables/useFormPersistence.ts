import { ref, watch, onMounted } from "vue";

const STORAGE_KEY = "recipe_form_data";

interface FormData {
  ingredients: string[];
  flavorTags: string[];
  cuisineTypes: string[];
  specialGroups: string[];
}

/**
 * 表单数据持久化 Composable
 * 自动保存和恢复表单输入数据到 localStorage
 */
export function useFormPersistence() {
  const formData = ref<FormData>({
    ingredients: [],
    flavorTags: [],
    cuisineTypes: [],
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
          ingredients: parsed.ingredients || [],
          flavorTags: parsed.flavorTags || [],
          cuisineTypes: parsed.cuisineTypes || [],
          specialGroups: parsed.specialGroups || [],
        };
      }
    } catch (error) {
      console.error("Failed to load form data from localStorage:", error);
    }
  }

  /**
   * 保存数据到 localStorage
   */
  function saveToStorage(data: FormData) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
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
        flavorTags: [],
        cuisineTypes: [],
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

  // 监听数据变化，自动保存
  watch(
    () => formData.value,
    (newValue) => {
      saveToStorage(newValue);
    },
    { deep: true },
  );

  return {
    formData,
    clearStorage,
  };
}
