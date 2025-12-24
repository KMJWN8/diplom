<template>
  <header class="app-header">
    <div class="container">
      <div class="header-content">
        <router-link to="/" class="logo">
          ИС Проблемы в регионе
        </router-link>
        
        <nav class="nav-menu">
          <router-link 
            to="/" 
            class="nav-link"
            active-class="active"
            exact-active-class="active"
          >
            Главная
          </router-link>
          <router-link 
            to="/dashboard" 
            class="nav-link"
            active-class="active"
          >
            Дашборд
          </router-link>
          <router-link 
            to="/report" 
            class="nav-link"
            active-class="active"
          >
            Отчет
          </router-link>
        </nav>
      </div>
    </div>
  </header>
</template>