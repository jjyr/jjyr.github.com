class RelativeTime extends HTMLElement {
  connectedCallback() {
    this.render();
  }

  render() {
    const datetime = this.getAttribute('datetime');
    if (!datetime) return;
    const date = new Date(datetime);
    if (isNaN(date.getTime())) return;

    const absDate = this.getAttribute('date') || datetime.slice(0, 10);
    const lang = (this.closest('[lang]')?.getAttribute('lang') || document.documentElement.lang || 'zh').toLowerCase();
    const isEn = lang.startsWith('en');
    const relDate = this.formatRelative(date, isEn);

    let relSpan = this.querySelector('.rel-date');
    let absSpan = this.querySelector('.abs-date');

    if (!relSpan || !absSpan) {
      this.innerHTML = `<span class="rel-date">${relDate}</span><span class="abs-date">${absDate}</span>`;
    } else {
      relSpan.textContent = relDate;
      absSpan.textContent = absDate;
    }
  }

  formatRelative(date, isEn) {
    const now = new Date();
    const diffMs = now - date;
    if (diffMs < 0) return isEn ? 'just now' : '刚刚';

    const diffDays = Math.floor(diffMs / 86400000);
    if (diffDays < 1) {
      const diffHours = Math.floor(diffMs / 3600000);
      if (diffHours < 1) return isEn ? 'just now' : '刚刚';
      if (isEn) {
        return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
      }
      return `${diffHours} 小时前`;
    }
    if (diffDays < 30) {
      if (isEn) {
        return diffDays === 1 ? '1 day ago' : `${diffDays} days ago`;
      }
      return `${diffDays} 天前`;
    }

    let months = (now.getFullYear() - date.getFullYear()) * 12 + (now.getMonth() - date.getMonth());
    if (now.getDate() < date.getDate()) {
      months--;
    }
    if (months < 1) months = 1;
    if (months < 12) {
      if (isEn) {
        return months === 1 ? '1 month ago' : `${months} months ago`;
      }
      return `${months} 个月前`;
    }

    let years = now.getFullYear() - date.getFullYear();
    if (now.getMonth() < date.getMonth() || (now.getMonth() === date.getMonth() && now.getDate() < date.getDate())) {
      years--;
    }
    if (years < 1) years = 1;
    if (isEn) {
      return years === 1 ? '1 year ago' : `${years} years ago`;
    }
    return `${years} 年前`;
  }
}

if (!customElements.get('relative-time')) {
  customElements.define('relative-time', RelativeTime);
}
