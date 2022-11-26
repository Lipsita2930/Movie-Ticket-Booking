import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HeaderComponent } from './header/header.component';
import { MainComponent } from './main/main.component';
import { MovieDetailsComponent } from './movie-details/movie-details.component';
import { OffersComponent } from './offers/offers.component';
import { UserPageComponent } from './user-page/user-page.component';


const routes: Routes = [
  {path:"header",component:HeaderComponent},
  {path:"",component:MainComponent},
  {path:"movie-details",component:MovieDetailsComponent},
  {path:"user-page",component: UserPageComponent},
  {path:"offers",component:OffersComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
