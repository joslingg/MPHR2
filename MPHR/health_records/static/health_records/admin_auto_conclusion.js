document.addEventListener("DOMContentLoaded", function () {
  const classificationSelect = document.querySelector("#id_health_classification");
  const conclusionInput = document.querySelector("#id_conclusion_text");

  function updateConclusion() {
    if (!classificationSelect || !conclusionInput) return;
    const selected = classificationSelect.options[classificationSelect.selectedIndex]?.text?.trim()?.toUpperCase();
    if (["I", "II", "III"].includes(selected)) {
      conclusionInput.value = "Đủ sức khoẻ làm việc";
    } else if (selected === "IV") {
      conclusionInput.value = "Làm việc hợp lý";
    } else {
      conclusionInput.value = "";
    }
  }

  if (classificationSelect) {
    classificationSelect.addEventListener("change", updateConclusion);
    updateConclusion(); // chạy 1 lần khi load
  }
});
