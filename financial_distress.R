library(magrittr)
library(data.table)
library(readxl)
library(memoise)
library(kit)

INPUT_FILE <-
  'H:/Data/non_standard/original/DG_EMPL_financial_distress.xls'

eval(bquote(stopifnot(file.exists(.(INPUT_FILE)))))

YEARS_QUARTERS <-
  expand.grid(1980:2030,
              paste0('Q',1:4)) %>% 
  {paste0(.[[1]],.[[2]])} %>% 
  sort()


# Functions ---------------------------------------------------------------

mem <- memoise::memoise

xlColnames <- mem(function(path_to_xls_file, sheet_name, country_level=FALSE)
  path_to_xls_file %>% 
    {suppressMessages(
      readxl::read_xls(., sheet=sheet_name,
                       n_max=ifelse(country_level,3,2),
                       col_names=FALSE))} %>% 
    t() %>% 
    {set_colnames(tail(.,-1),
                  head(.,1))} %>% 
    as.data.table() %>% 
    .[, excel_colnum := .I + 1] %>% 
    `if`(country_level,
         setnames(.,2,'geo') %>% 
           setcolorder(.,c(1,3,2)),
         .))

xlData <- mem(function(path_to_xls_file, sheet_name, country_level=FALSE)
  path_to_xls_file %>% 
    {suppressMessages(
      readxl::read_xls(., sheet=sheet_name,
                       skip=ifelse(country_level,3,2),
                       col_names=FALSE))} %>% 
    as.data.table() %>% 
    {stopifnot(.[[1]] %>% inherits("POSIXct"));.} %>% 
    .[, year_month := ...1 %>% 
        {paste0(format(.,"%Y"),"M",format(.,"%m"))}])

xlColumn <- function(path_to_xls_file=INPUT_FILE,
                     sheet_name,
                     country_level=FALSE,
                     col_id1_string='12', col_id2_string,
                     moving_avg=TRUE,
                     moving_num=12,
                     new_name=paste(sheet_name,col_id1_string,col_id2_string,
                                    ifelse(moving_avg,'movavg','orig'),
                                    sep='.')) {
  message('\nRunning xlColumn() with the following parameters:',
          match.call() %>% tail(-1) %>% 
            {paste('\n',names(.),'=',as.character(.))})
  dt__selected_xl_cols <-
    xlColnames(path_to_xls_file, sheet_name, country_level) %>% 
    .[.[[1]]==col_id1_string & .[[2]]==col_id2_string] %>% 
    `if`(nrow(.)==0,
         stop('No Excel column found in\n',path_to_xls_file,
              '\nfor sheet name = ',sheet_name,
              "\nfor column header's first row = ",col_id1_string,
              "\nfor column header's ",ifelse(country_level,'third','second'),' row = ',col_id2_string),
         .)
  path_to_xls_file %>% 
    xlData(sheet_name, country_level) %>% 
    {data.table(.$year_month,
                .[, dt__selected_xl_cols$excel_colnum, with=FALSE])} %>% 
    {`if`('geo' %in% colnames(dt__selected_xl_cols),
          setnames(.,colnames(.)[-1],dt__selected_xl_cols$geo) %>% 
            melt(id.vars=1, variable.name='geo', variable.factor=FALSE,
                 value.name='val') %>% 
            setorderv(setdiff(colnames(.),'val')),
          setnames(.,colnames(.)[2],'val'))} %>% 
    `if`(moving_avg,
         .[, val := frollmean(val, moving_num, algo='exact'),
           by = `if`('geo' %in% colnames(.), geo)],
         .) %>% 
    setnames(setdiff(colnames(.),'geo'),
             c('year_month',new_name))
}

xlColumnsAdded <- function(arg_list, moving_avg=TRUE, moving_num=12, new_name) {
  dt1 <- do.call(xlColumn, arg_list[[1]])
  dt2 <- do.call(xlColumn, arg_list[[2]])
  dt1_indic_name <- setdiff(colnames(dt1),c('year_month','geo'))
  dt2_indic_name <- setdiff(colnames(dt2),c('year_month','geo'))
  merge(dt1, dt2, by=intersect(colnames(dt1),
                               colnames(dt2))) %>% 
    .[, (new_name) := get(dt1_indic_name)+get(dt2_indic_name)] %>% 
    .[, c(dt1_indic_name,dt2_indic_name) := NULL] %>% 
    `if`(moving_avg,
         .[, (new_name) := frollmean(get(new_name), moving_num, algo='exact')],
         .) 
}

yearMonthToYearQuarter <- function(year_month)
  year_month %>%
  substr(6,7) %>%
  as.integer() %>%
  {kit::nif(. %in% 1:3, 1L,
            . %in% 4:6, 2L,
            . %in% 7:9, 3L,
            . %in% 10:12, 4L,
            default = NA_integer_)} %>%
  paste0(substr(year_month,1,4),"Q",.)

year_quarter_minus_n_quarters <- function(year_quarter,n) {
  yq <- unique(year_quarter)
  if (length(yq)!=1 || any(!grepl('^\\d{4}Q[1-4]$',yq))) {
    stop('`year_quarter` should be a single date in the format YYYYQN, ',
         'instead received: ')
    str(year_quarter)
  }
  data.table(current=YEARS_QUARTERS,
             previous=YEARS_QUARTERS %>% shift(n,type='lag')) %>% 
    .[current==yq] %>% 
    .$previous
}


# Actions -----------------------------------------------------------------

EU_indicators <-
  list(
    xlColumn(sheet_name='EU',col_id2_string='MM',
             new_name='Running into debt'),
    xlColumn(sheet_name='EU',col_id2_string='M',
             new_name='Having to draw on savings'),
    xlColumnsAdded(list(list(sheet_name='EU_RE1',col_id2_string='MM',moving_avg=FALSE),
                        list(sheet_name='EU_RE1',col_id2_string='M',moving_avg=FALSE)),
                   new_name='lowest income quartile'),
    xlColumnsAdded(list(list(sheet_name='EU_RE2',col_id2_string='MM',moving_avg=FALSE),
                        list(sheet_name='EU_RE2',col_id2_string='M',moving_avg=FALSE)),
                   new_name='second quartile'),
    xlColumnsAdded(list(list(sheet_name='EU_RE3',col_id2_string='MM',moving_avg=FALSE),
                        list(sheet_name='EU_RE3',col_id2_string='M',moving_avg=FALSE)),
                   new_name='third quartile'),
    xlColumnsAdded(list(list(sheet_name='EU_RE4',col_id2_string='MM',moving_avg=FALSE),
                        list(sheet_name='EU_RE4',col_id2_string='M',moving_avg=FALSE)),
                   new_name='top quartile')
  ) %>% 
  Reduce(\(x1,x2) merge(x1,x2,by='year_month'),
         x=.) %>% 
  .[, 'Financial distress - Total' := 
      get('Running into debt') + get('Having to draw on savings')] %>% 
  setcolorder(c('year_month',
                'Financial distress - Total')) %T>% 
  fwrite('Financial_distress_EU_monthly.csv')

Country_indicators <-
  list(
    xlColumn(sheet_name='financial stress by country1',
             country_level=TRUE,
             col_id2_string='RE1',
             moving_num=3,
             new_name='Reported financial distress in lowest income quartile'),
    xlColumn(sheet_name='financial stress by country2',
             country_level=TRUE,
             col_id2_string='RE1',
             moving_num=3,
             new_name='Reported financial distress in lowest income quartile')
  ) %>% 
  rbindlist() %>% 
  .[, year_quarter := yearMonthToYearQuarter(year_month)] %>% 
  .[, .(`Reported financial distress in lowest income quartile` =
          mean(`Reported financial distress in lowest income quartile`)),
    by=.(geo,year_quarter)] %>% 
  .[!is.na(`Reported financial distress in lowest income quartile`)] %>% 
  .[, num_of_available_countries :=
      length(`Reported financial distress in lowest income quartile`),
    by=year_quarter] %>%
  .[, latest_year_quarter_with_at_least_15_countries :=
      max(year_quarter[num_of_available_countries>=15])] %>% 
  .[year_quarter==latest_year_quarter_with_at_least_15_countries |
      year_quarter==
      year_quarter_minus_n_quarters(latest_year_quarter_with_at_least_15_countries,4) |  # 1 year earlier
      year_quarter==
      year_quarter_minus_n_quarters(latest_year_quarter_with_at_least_15_countries,44)  # 11 years earlier
  ] %T>% 
  fwrite('Financial_distress_countries_quarterly__full.csv') %>% 
  dcast(geo ~ year_quarter,
        fun.aggregate=identity,
        fill=NA_real_,
        value.var='Reported financial distress in lowest income quartile') %>% 
  {
    latest_two_periods <-
      colnames(.) %>% 
      setdiff('geo') %>% 
      sort() %>% 
      tail(2)
    new_col <-
      paste('Difference:',latest_two_periods[2],'minus',latest_two_periods[1])
    .[, (new_col) := get(latest_two_periods[2]) - get(latest_two_periods[1])] %>% 
      setorderv(new_col, order=-1) %>% 
      .[, country_group :=
          get(new_col) %>% 
          {kit::nif(. < -1.1, 'decrease',
                    . <  1.1, 'stable',
                    . <  3.0, 'increase',
                    . >=  3.0, 'strong increase',
                    default = NA_character_)}]
  } %>% 
  setcolorder('country_group') %T>% 
  fwrite('Financial_distress_countries_quarterly.csv')



