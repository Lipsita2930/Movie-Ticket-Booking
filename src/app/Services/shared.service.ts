import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
  movieDetails:any;
 
  constructor(private snackBar:MatSnackBar) {}
  
  setAllDetails(movie:any){
   this.movieDetails=movie;
  }

  getMovieDetails(){
    return this.movieDetails;
  }
  
  sharedNotification(display:string,Buttontext:string){
    this.snackBar.open(display,Buttontext,{
      duration:5000, 
      horizontalPosition:'center',
      verticalPosition:'bottom',
    })
  }
 
}
