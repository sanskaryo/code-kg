function loadData() {
  if (window && window.user) {
    return window.user.name;
  }
  return "guest";
}

const runApp = () => {
  const name = loadData();
  return name;
};
