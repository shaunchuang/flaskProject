import re
from flask.helpers import url_for
from myapp import app
from flask import render_template, request, redirect
from myapp.model import predict, data_collect, result_compute
from myapp.mysql_model import create_url
from myapp.init_conn import connection
import math


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/predictPrice', methods=['GET', 'POST'])
def predictPrice():
    car_brand = ['Aston Martin', 'Audi', 'Bentley', 'BMW', 'Citroen', 'Ferrari', 'Ford', 'Hyundai', 'Infiniti', 'Jaguar', 'Kia', 'Lamborghini', 'Land Rover', 'Lexus', 'Lotus', 'Mercedes-Benz', 'Mahindra',
                 'Maserati', 'Mazda', 'McLaren', 'Mini', 'Mitsubishi', 'Morgan', 'Nissan', 'Peugeot', 'Porsche', 'Rolls-Royce', 'Skoda', 'Ssangyong', 'Subaru', 'Suzuki', 'Tesla', 'Toyota', 'Volkswagen', 'Volvo']
    # try:
    if request.method == 'POST':
        form = request.form
        form = dict(form)
        input = data_collect(form)
        result = predict(input)
        result = result_compute(result)
        print(result)
        return render_template('predictPrice_result.html', form=form, car_brand=car_brand, result=result)
    # except:
    #     exe_info='輸入格式錯誤請重新輸入'
    #     return render_template('predictPrice_form.html',exe_info=exe_info, car_brand=car_brand)
    # finally:
    #     return render_template('predictPrice_form.html', car_brand=car_brand)
    return render_template('predictPrice_form.html', car_brand=car_brand)


@app.route('/loan')
def loan():
    price = request.args.get('price', type=float)
    return render_template('loan.html', price=price)


@app.route('/bestCarForm',  methods=['GET', 'POST'])
def bestCarForm():
    if request.method == 'POST':
        form = dict(request.form)
        cbrand = form['brand']
        cyear = form['cyear']
        ckm = form['km']
        return redirect(url_for('bestCarResult', brand=cbrand, year=cyear, mileage=ckm))
    return render_template('bestCar_form.html')


@app.route('/bestCarResult')
def bestCarResult():

    page = request.args.get('page', 1, type=int)  # init page=1

    # Normal: TOYOTA,
    # FORD, HONDA, NISSAN, MITSUBISHI, MAZADA, LUXGEN, HYUNDAI, KIA
    # Advanced: SKODA, SUZUKI, SUBARU, VOLKSWAGEN, PEUGEOT, CITROEN, RENAULT, OPEL,
    # Luxury: LEXUS, INFINITI, JAGUAR, TESLA, VOLVO, BENZ, BMW, AUDI, PORSCHE, MASERATI, MCLAREN, FERRARI, LAMBORGHINI
    cbrand = request.args.get('brand', None)
    cyear = request.args.get('year', None)
    ckm = request.args.get('mileage', None)

    brandsql = None
    if cbrand == 'normal':
        brandsql = 'carBrand="TOYOTA" or carBrand="FORD" or carBrand="HONDA" or carBrand="NISSAN" or carBrand="MITSUBISHI" or carBrand="MAZADA" or carBrand="LUXGEN" or carBrand="HYUNDAI" or carBrand="KIA"'
    if cbrand == 'advanced':
        brandsql = 'carBrand="SKODA" or carBrand="SUZUKI" or carBrand="SUBARU" or carBrand="VOLKSWAGEN" or carBrand="PEUGEOT" or carBrand="CITROEN" or carBrand="RENAULT or carBrand="OPEL"'
    if cbrand == 'luxury':
        brandsql = 'carBrand="LEXUS" or carBrand="INFINITI" or carBrand="JAGUAR" or carBrand="TESLA" or carBrand="VOLVO" or carBrand="BENZ" or carBrand="BMW" or carBrand="AUDI" or carBrand="PORSCHE" or carBrand="MASERATI" or carBrand="MCLAREN" or carBrand="FERRARI" or carBrand="LAMBORGHINI"'

    yearsql = None
    if cyear == '5':
        yearsql = 'carYear >= 2016'
    if cyear == '510':
        yearsql = 'carYear >= 2011 and carYear <= 2016'
    if cyear == '10':
        yearsql = 'carYear <= 2011'

    kmsql = None
    if ckm == '3':
        kmsql = 'carMileage <= 30000'
    if ckm == '310':
        kmsql = 'carMileage >= 30000 and carMileage <= 100000'
    if ckm == '10':
        kmsql = 'carMileage >= 100000'

    cr = connection.cursor()    # init cursor
    sqlitems = f'SELECT COUNT(*) AS items FROM car_list WHERE ({brandsql}) and ({yearsql}) and ({kmsql})'

    cr.execute(sqlitems)        # execute sql query
    rows = cr.fetchone()        # get sql result
    items = rows['items']       # to get total items
    total_pages = math.ceil(items/9)   # get total pages
    limit = 9                   # limited 9 items in one page

    if page < total_pages:      # user's page < totalpages then offset -> user's page
        offset = page*limit - limit
    else:
        # user's page >= totalpages then offest -> total page
        offset = total_pages*limit - limit

    cur = connection.cursor()   # init cursor
    # from offset value to query 9 items
    sqltest = f'SELECT * FROM car_list WHERE ({brandsql}) and ({yearsql}) and ({kmsql}) LIMIT {limit} OFFSET {offset}'
    cur.execute(sqltest)        # execute sql query
    result = cur.fetchall()     # get sql result

    for r in result:
        r['car_url'] = create_url(r)    # create car link from defined function

    return render_template('bestCar_result.html', result=result, page=page, totalpages=total_pages, brand=cbrand, year=cyear, mileage=ckm)
