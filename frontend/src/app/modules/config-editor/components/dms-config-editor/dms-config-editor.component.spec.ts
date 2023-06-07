import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DmsConfigEditorComponent } from './dms-config-editor.component';

describe('DmsConfigEditorComponent', () => {
  let component: DmsConfigEditorComponent;
  let fixture: ComponentFixture<DmsConfigEditorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DmsConfigEditorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DmsConfigEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
