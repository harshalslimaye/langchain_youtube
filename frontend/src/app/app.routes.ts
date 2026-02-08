import { Routes } from '@angular/router';

export const routes: Routes = [
    {   
        path: '',
        loadComponent: () => import('./search/search').then(m => m.SearchComponent) 
    },
    {
        path: ':videoId',
        loadComponent: () => import('./query/query').then(m => m.QueryComponent)
    }
];
