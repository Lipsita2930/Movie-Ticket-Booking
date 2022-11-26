import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ApiConsumingService } from '../Services/api-consuming.service';
import { Movies } from '../Utilities/Movie';

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.css']
})
export class MainComponent implements OnInit {
  movies: Movies[] = [];
  constructor(private services: ApiConsumingService, private router: Router) { }

  ngOnInit(): void {
    this.getAllData();
  }

  getAllData() {
    this.services.getMovieDetails().subscribe((data: Movies[]) => {
      this.movies = data;
    })
  }


  btnClickListener(movie: any) {
    this.router.navigate(['/movie-details',movie]);
  }

  searchText: string = '';
  onSearchTextEntered(searchValue: string) {
    this.searchText = searchValue;
    console.log(this.searchText);
  }

}


