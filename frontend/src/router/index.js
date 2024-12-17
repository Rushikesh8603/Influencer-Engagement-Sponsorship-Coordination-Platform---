// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import UserRegister from '../views/UserRegister.vue';
import SponsorPage from '../views/SponsorPage.vue';
import campain from '../views/campain.vue';
import sponsorSignup from '../views/sponsorSignup.vue';
import EditCampaign from '../views/EditCampaign.vue';
import influencer from '../views/influencer.vue';

import activeCampaigns from '../views/active-campaigns.vue';
import influencer_requests from '../views/influencer_requests.vue';

import search_influ_from_spo from '../views/search_influ_from_spo.vue';
import sponsor_request from '../views/sponsor_request.vue';
import admin from '../views/admin.vue';
import Export from '../views/Export.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/Export',          // Home route at '/'
      name: 'Export',
      component: Export,
    },
    {
      path: '/',          // Home route at '/'
      name: 'home',
      component: HomeView,
    },
    {
      path: '/admin',          // Home route at '/'
      name: 'admin',
      component: admin,
    },
    {
      path: '/UserRegister',  // Register route at '/register'
      name: 'UserRegister',
      component: UserRegister,
    },
    {
      path:'/campaign',
      name:'campaign',
      component:campain,
    },
    {
      path:"/sponsor-home",  // this is a spnsor home page route 
      name:"SponsorPage",
      component:SponsorPage,
    },
    {
      path:"/sponsorsignup",
      name :"sponsorsignup",
      component:sponsorSignup,
    },
    {
      path: '/campaign/edit/:id',
      name: 'EditCampaign',
      component: EditCampaign,
    },
    {
      path:'/iDash',
      name: 'iDash',
      component:influencer,
    },
    {
      path:"/active-campaigns",
      name:"active-campaigns",
      component:activeCampaigns,
    },
  
    {
      path:"/influencer_requests",
      name:"influencer_requests",
      component:influencer_requests,
    },
    {
      path: '/search_influ_from_spo/:id',
      name: 'search_influ_from_spo',
      component: search_influ_from_spo,
    },
    {
      path: '/sponsor_request',
      name: 'sponsor_request',
      component: sponsor_request,
    },
  ],
  
});


export default router;
// 