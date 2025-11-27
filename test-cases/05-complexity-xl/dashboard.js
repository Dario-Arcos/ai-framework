/**
 * Dashboard Component - Large File to Trigger XL Complexity
 * This file is intentionally large (>600 lines) to trigger ⚠️ Complexity observation
 */

class Dashboard {
  constructor(config) {
    this.config = config;
    this.widgets = [];
    this.data = {};
    this.filters = {};
    this.cache = new Map();
    this.eventListeners = new Map();
    this.state = {
      loading: false,
      error: null,
      lastUpdate: null
    };
  }

  // Widget Management (Lines 20-120)
  addWidget(widget) {
    this.widgets.push(widget);
    this.renderWidget(widget);
  }

  removeWidget(widgetId) {
    this.widgets = this.widgets.filter(w => w.id !== widgetId);
    this.destroyWidget(widgetId);
  }

  renderWidget(widget) {
    const container = document.getElementById('dashboard');
    const element = document.createElement('div');
    element.className = 'widget';
    element.id = `widget-${widget.id}`;
    element.innerHTML = this.getWidgetTemplate(widget);
    container.appendChild(element);
  }

  destroyWidget(widgetId) {
    const element = document.getElementById(`widget-${widgetId}`);
    if (element) element.remove();
  }

  getWidgetTemplate(widget) {
    return `
      <div class="widget-header">
        <h3>${widget.title}</h3>
        <button onclick="dashboard.removeWidget('${widget.id}')">×</button>
      </div>
      <div class="widget-body" id="widget-body-${widget.id}">
        ${widget.content || 'Loading...'}
      </div>
    `;
  }

  // Data Fetching (Lines 60-160)
  async fetchData(endpoint, params = {}) {
    const cacheKey = `${endpoint}-${JSON.stringify(params)}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    this.state.loading = true;
    try {
      const response = await fetch(this.buildUrl(endpoint, params));
      const data = await response.json();
      this.cache.set(cacheKey, data);
      this.state.lastUpdate = new Date();
      return data;
    } catch (error) {
      this.state.error = error.message;
      throw error;
    } finally {
      this.state.loading = false;
    }
  }

  buildUrl(endpoint, params) {
    const url = new URL(endpoint, this.config.baseUrl);
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
    return url.toString();
  }

  // Chart Rendering (Lines 90-190)
  renderChart(containerId, data, options = {}) {
    const container = document.getElementById(containerId);
    const canvas = document.createElement('canvas');
    container.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    const width = container.clientWidth;
    const height = container.clientHeight;
    canvas.width = width;
    canvas.height = height;

    this.drawChart(ctx, data, options, width, height);
  }

  drawChart(ctx, data, options, width, height) {
    const padding = 40;
    const chartWidth = width - (padding * 2);
    const chartHeight = height - (padding * 2);

    // Draw axes
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // Draw data points
    const maxValue = Math.max(...data.map(d => d.value));
    data.forEach((point, index) => {
      const x = padding + (chartWidth / data.length) * index;
      const y = height - padding - (point.value / maxValue) * chartHeight;

      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  // Table Rendering (Lines 140-240)
  renderTable(containerId, data, columns) {
    const container = document.getElementById(containerId);
    const table = document.createElement('table');
    table.className = 'dashboard-table';

    // Header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    columns.forEach(col => {
      const th = document.createElement('th');
      th.textContent = col.label;
      th.onclick = () => this.sortTable(data, col.key);
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body
    const tbody = document.createElement('tbody');
    data.forEach(row => {
      const tr = document.createElement('tr');
      columns.forEach(col => {
        const td = document.createElement('td');
        td.textContent = this.formatCell(row[col.key], col.format);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    container.innerHTML = '';
    container.appendChild(table);
  }

  sortTable(data, key) {
    return data.sort((a, b) => {
      if (a[key] < b[key]) return -1;
      if (a[key] > b[key]) return 1;
      return 0;
    });
  }

  formatCell(value, format) {
    if (!format) return value;

    switch (format) {
      case 'currency':
        return `$${value.toFixed(2)}`;
      case 'percentage':
        return `${(value * 100).toFixed(1)}%`;
      case 'date':
        return new Date(value).toLocaleDateString();
      default:
        return value;
    }
  }

  // Filters (Lines 210-310)
  applyFilter(key, value) {
    this.filters[key] = value;
    this.refreshData();
  }

  removeFilter(key) {
    delete this.filters[key];
    this.refreshData();
  }

  clearFilters() {
    this.filters = {};
    this.refreshData();
  }

  async refreshData() {
    const promises = this.widgets.map(widget => {
      return this.fetchData(widget.endpoint, this.filters);
    });

    const results = await Promise.all(promises);
    results.forEach((data, index) => {
      this.updateWidget(this.widgets[index].id, data);
    });
  }

  updateWidget(widgetId, data) {
    const widget = this.widgets.find(w => w.id === widgetId);
    if (!widget) return;

    const bodyElement = document.getElementById(`widget-body-${widgetId}`);
    if (widget.type === 'chart') {
      this.renderChart(bodyElement.id, data, widget.chartOptions);
    } else if (widget.type === 'table') {
      this.renderTable(bodyElement.id, data, widget.columns);
    } else {
      bodyElement.innerHTML = JSON.stringify(data, null, 2);
    }
  }

  // Event Handling (Lines 260-360)
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event).push(callback);
  }

  off(event, callback) {
    if (!this.eventListeners.has(event)) return;
    const listeners = this.eventListeners.get(event);
    const index = listeners.indexOf(callback);
    if (index > -1) {
      listeners.splice(index, 1);
    }
  }

  emit(event, data) {
    if (!this.eventListeners.has(event)) return;
    this.eventListeners.get(event).forEach(callback => {
      callback(data);
    });
  }

  // Export Functionality (Lines 310-410)
  exportToCSV(widgetId) {
    const widget = this.widgets.find(w => w.id === widgetId);
    if (!widget || widget.type !== 'table') return;

    const data = this.data[widgetId];
    const csv = this.convertToCSV(data, widget.columns);
    this.downloadFile(csv, `${widget.title}.csv`, 'text/csv');
  }

  convertToCSV(data, columns) {
    const headers = columns.map(c => c.label).join(',');
    const rows = data.map(row => {
      return columns.map(c => row[c.key]).join(',');
    });
    return [headers, ...rows].join('\n');
  }

  downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  // Settings (Lines 360-460)
  saveSettings() {
    const settings = {
      widgets: this.widgets.map(w => ({
        id: w.id,
        type: w.type,
        position: w.position,
        config: w.config
      })),
      filters: this.filters,
      theme: this.config.theme
    };
    localStorage.setItem('dashboard-settings', JSON.stringify(settings));
  }

  loadSettings() {
    const saved = localStorage.getItem('dashboard-settings');
    if (!saved) return;

    const settings = JSON.parse(saved);
    settings.widgets.forEach(w => this.addWidget(w));
    this.filters = settings.filters || {};
    this.config.theme = settings.theme || 'light';
  }

  resetSettings() {
    localStorage.removeItem('dashboard-settings');
    this.widgets = [];
    this.filters = {};
    this.render();
  }

  // Responsive Layout (Lines 410-510)
  handleResize() {
    this.widgets.forEach(widget => {
      this.updateWidgetSize(widget.id);
    });
  }

  updateWidgetSize(widgetId) {
    const element = document.getElementById(`widget-${widgetId}`);
    if (!element) return;

    const width = element.clientWidth;
    const widget = this.widgets.find(w => w.id === widgetId);

    if (width < 400) {
      element.classList.add('mobile');
    } else if (width < 768) {
      element.classList.add('tablet');
    } else {
      element.classList.add('desktop');
    }
  }

  // Drag and Drop (Lines 460-560)
  enableDragDrop() {
    this.widgets.forEach(widget => {
      const element = document.getElementById(`widget-${widget.id}`);
      element.draggable = true;
      element.ondragstart = (e) => this.handleDragStart(e, widget.id);
      element.ondragover = (e) => this.handleDragOver(e);
      element.ondrop = (e) => this.handleDrop(e, widget.id);
    });
  }

  handleDragStart(event, widgetId) {
    event.dataTransfer.setData('widgetId', widgetId);
  }

  handleDragOver(event) {
    event.preventDefault();
  }

  handleDrop(event, targetWidgetId) {
    event.preventDefault();
    const sourceWidgetId = event.dataTransfer.getData('widgetId');
    this.swapWidgets(sourceWidgetId, targetWidgetId);
  }

  swapWidgets(id1, id2) {
    const idx1 = this.widgets.findIndex(w => w.id === id1);
    const idx2 = this.widgets.findIndex(w => w.id === id2);
    [this.widgets[idx1], this.widgets[idx2]] = [this.widgets[idx2], this.widgets[idx1]];
    this.render();
  }

  // Lifecycle (Lines 510-610)
  init() {
    this.loadSettings();
    this.setupEventListeners();
    this.render();
    this.startAutoRefresh();
  }

  setupEventListeners() {
    window.addEventListener('resize', () => this.handleResize());
    this.on('data-updated', (data) => {
      console.log('Dashboard data updated', data);
    });
  }

  render() {
    const container = document.getElementById('dashboard');
    container.innerHTML = '<h1>Dashboard</h1>';
    this.widgets.forEach(widget => this.renderWidget(widget));
    this.enableDragDrop();
  }

  startAutoRefresh() {
    if (this.config.autoRefresh) {
      this.refreshInterval = setInterval(() => {
        this.refreshData();
      }, this.config.refreshInterval || 60000);
    }
  }

  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }

  destroy() {
    this.stopAutoRefresh();
    this.widgets = [];
    this.cache.clear();
    this.eventListeners.clear();
    window.removeEventListener('resize', this.handleResize);
  }

  // Utility Methods (Lines 580-650)
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  }

  // Additional padding to reach >600 lines
  generateId() {
    return Math.random().toString(36).substr(2, 9);
  }

  log(message, level = 'info') {
    const timestamp = new Date().toISOString();
    console[level](`[${timestamp}] ${message}`);
  }

  validateConfig(config) {
    const required = ['baseUrl'];
    required.forEach(key => {
      if (!config[key]) {
        throw new Error(`Missing required config: ${key}`);
      }
    });
    return true;
  }
}

module.exports = Dashboard;
